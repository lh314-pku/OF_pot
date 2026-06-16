from sqlalchemy.orm import Session
from routes.base import BaseCommand, CommandRegistry
from db import engine
from models import PotDB, CTX, UTC_Plus_8, now_plus_8

import re
import datetime


def parse_time(time_str: str, existing: datetime.datetime) -> datetime.datetime | None:
    """逐级解析时间字符串，返回 UTC+8 的 datetime 或 None 表示格式错误。

    支持格式（从具体到模糊）：
      YYYY-MM-DD HH:MM  → 完整日期时间
      YYYY-MM-DD HH     → 完整日期 + 小时
      MM-DD HH:MM       → 月日 + 时分（年份取 existing 的年份）
      MM-DD HH          → 月日 + 小时（年份取 existing 的年份）
      YYYY-MM-DD        → 仅日期，保留 existing 的时间
      MM-DD             → 仅月日，保留 existing 的时间和年份
      HH:MM             → 仅时分，日期取今天
      HH                → 仅小时，日期取今天
    """
    now = now_plus_8()
    today = now.date()

    patterns = [
        # (regex, handler)
        (r"^(\d{4})-(\d{2})-(\d{2})\s+(\d{1,2}):(\d{2})$",
         lambda g: datetime.datetime(int(g[0]), int(g[1]), int(g[2]), int(g[3]), int(g[4]), tzinfo=UTC_Plus_8)),
        (r"^(\d{4})-(\d{2})-(\d{2})\s+(\d{1,2})$",
         lambda g: datetime.datetime(int(g[0]), int(g[1]), int(g[2]), int(g[3]), tzinfo=UTC_Plus_8)),
        (r"^(\d{1,2})-(\d{2})\s+(\d{1,2}):(\d{2})$",
         lambda g: datetime.datetime(existing.year, int(g[0]), int(g[1]), int(g[2]), int(g[3]), tzinfo=UTC_Plus_8)),
        (r"^(\d{1,2})-(\d{2})\s+(\d{1,2})$",
         lambda g: datetime.datetime(existing.year, int(g[0]), int(g[1]), int(g[2]), tzinfo=UTC_Plus_8)),
        (r"^(\d{4})-(\d{2})-(\d{2})$",
         lambda g: datetime.datetime(int(g[0]), int(g[1]), int(g[2]), existing.hour, existing.minute, tzinfo=UTC_Plus_8)),
        (r"^(\d{1,2})-(\d{2})$",
         lambda g: datetime.datetime(existing.year, int(g[0]), int(g[1]), existing.hour, existing.minute, tzinfo=UTC_Plus_8)),
        (r"^(\d{1,2}):(\d{2})$",
         lambda g: datetime.datetime(today.year, today.month, today.day, int(g[0]), int(g[1]), tzinfo=UTC_Plus_8)),
        (r"^(\d{1,2})$",
         lambda g: datetime.datetime(today.year, today.month, today.day, int(g[0]), tzinfo=UTC_Plus_8)),
    ]

    for pattern, handler in patterns:
        m = re.match(pattern, time_str)
        if m:
            try:
                return handler(m.groups())
            except ValueError:
                return None

    return None


class SetTimeCommand(BaseCommand):
    name = "/settime"
    pattern = "/settime [id] start|expire [时间]"
    help = "修改锅的开始/过期时间（仅限发起人），支持 HH / HH:MM / MM-DD / YYYY-MM-DD 等格式"
    detail = (
        "修改锅的开始时间或过期时间，仅发起人可操作。\n"
        "支持逐级时间格式（越具体优先级越高）：\n"
        "  18          → 今天 18:00\n"
        "  18:30       → 今天 18:30\n"
        "  12-31       → 12月31日，保留锅原有的时分\n"
        "  2025-12-31  → 2025年12月31日，保留锅原有的时分\n"
        "  12-31 18    → 12月31日 18:00\n"
        "  12-31 18:30 → 12月31日 18:30\n"
        "  2025-12-31 18:30 → 完整日期时间\n"
        "示例：/settime 1 expire 23:59"
    )
    re = re.compile(r"^/settime\s+(\d+)\s+(start|expire)\s+(.+)$")

    async def handle(self, ctx: CTX):
        msg = ctx.msg
        member = ctx.member

        assert self.re is not None
        mat = self.re.match(msg)
        if not mat:
            return (
                "格式：/settime [id] start|expire [时间]\n"
                "支持的时间格式：\n"
                "  18        → 今天 18:00\n"
                "  18:30     → 今天 18:30\n"
                "  12-31     → 12月31日，保留当前时间\n"
                "  2025-12-31 → 2025年12月31日，保留当前时间\n"
                "  12-31 18:30 → 12月31日 18:30\n"
                "  2025-12-31 18:30 → 完整日期时间"
            )

        pot_id = int(mat.group(1))
        time_field = mat.group(2)  # "start" or "expire"
        time_str = mat.group(3).strip()

        with Session(engine) as session:
            target = session.query(PotDB).filter(
                PotDB.id == pot_id,
                PotDB.expire_time > now_plus_8(),
            ).first()

            if not target:
                return "锅不存在"

            if target.creator["user_id"] != member.user_id:
                return "只有发起人可以修改时间"

            existing = getattr(target, f"{time_field}_time")
            new_time = parse_time(time_str, existing)

            if new_time is None:
                return "时间格式错误或日期无效，请检查输入"

            if time_field == "start":
                target.start_time = new_time
            else:
                target.expire_time = new_time

            session.add(target)
            session.commit()

        field_name = "开始时间" if time_field == "start" else "过期时间"
        display = new_time.strftime("%Y-%m-%d %H:%M")
        return f"已将 {pot_id} 的{field_name}修改为 {display}"


CommandRegistry.register(SetTimeCommand)
