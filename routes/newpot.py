import asyncio

from sqlalchemy.orm import Session
from routes.base import BaseCommand, CommandRegistry
from db import engine
from models import PotDB, CTX
from api import get_member_name

import re

class NewPotCommand(BaseCommand):
    name = "/newpot"
    help = "创建锅"
    pattern = "/newpot [内容] (@...)"
    detail = "创建新锅，可 @ 多人自动加入。\n示例：/newpot 晚上吃饭 @小明 @小红"
    re = re.compile(r"^/newpot\s+(.+)$")

    async def handle(self, ctx: CTX):
        msg = ctx.msg
        member = ctx.member

        assert self.re is not None
        mat = self.re.match(msg)
        if not mat:
            return "格式：/newpot 内容 [@某人 ...]"

        full_text = mat.group(1)

        # 提取所有被 @ 的用户 ID
        at_ids = [int(x) for x in re.findall(r"\[CQ:at,qq=(\d+)\]", full_text)]

        # 去掉 @mention 得到纯描述
        detail = re.sub(r"\s*\[CQ:at,qq=\d+\]", "", full_text).strip()

        if not detail:
            return "格式：/newpot 内容 [@某人 ...]"

        # 并发查询被 @ 用户的群名片/昵称
        at_names = await asyncio.gather(
            *[get_member_name(ctx.ws, ctx.group_id, uid) for uid in at_ids],
        )

        # 构建成员列表（去重，发起人排第一）
        members = [member.to_dict()]
        seen_ids = {member.user_id}
        for uid, name in zip(at_ids, at_names):
            if uid not in seen_ids:
                members.append({"user_id": uid, "nickname": name})
                seen_ids.add(uid)

        with Session(engine) as session:
            pot = PotDB(
                creator=member.to_dict(),
                detail=detail,
                members=members,
            )
            session.add(pot)
            session.commit()
            session.refresh(pot)

        extra = f"，已自动加入 {len(at_ids)} 人" if at_ids else ""
        return f"创建成功 ID:{pot.id}{extra}"


CommandRegistry.register(NewPotCommand)
