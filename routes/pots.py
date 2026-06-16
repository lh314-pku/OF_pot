from sqlalchemy.orm import Session
from routes.base import BaseCommand, CommandRegistry
from db import engine
from models import PotDB, CTX, now_plus_8, format_time_smart

import re

class PotsCommand(BaseCommand):
    name = "/pots"
    help = "查看锅列表"
    re = re.compile(r"^/pots$")

    async def handle(self, ctx: CTX):
        now = now_plus_8()

        with Session(engine) as session:
            pots = session.query(PotDB).filter(PotDB.expire_time > now).all()
            if not pots:
                return "当前没有锅"
            return "\n===========\n".join(self._get_detail(p, now) for p in pots)

    @staticmethod
    def _get_detail(pot: PotDB, now):
        start_str = format_time_smart(pot.start_time, now)
        expire_str = format_time_smart(pot.expire_time, now)
        return (
            f"ID: {pot.id}\n"
            f"内容: {pot.detail}\n"
            f"发起人: {pot.creator['nickname']}\n"
            f"成员: {', '.join([m['nickname'] for m in pot.members])}\n"
            f"开始时间: {start_str}\n"
            f"过期时间: {expire_str}"
        )


CommandRegistry.register(PotsCommand)
