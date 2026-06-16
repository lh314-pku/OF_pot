from sqlalchemy.orm import Session
from routes.base import BaseCommand, CommandRegistry
from db import engine
from models import PotDB, CTX, now_plus_8

import re

# at的纯文本表现为：[CQ:at,qq=3793626092]

class TransferCommand(BaseCommand):
    name = "/transfer"
    pattern = "/transfer [id] at某人"
    help = "转让发起人给某人（仅限当前发起人）"
    detail = "将发起人转让给锅内的另一成员。仅当前发起人可操作，被转让人必须在锅中。"
    re = re.compile(r"^/transfer\s+(\d+)\s+\[CQ:at,qq=(\d+)\]$")

    async def handle(self, ctx: CTX):
        msg = ctx.msg
        member = ctx.member

        assert self.re is not None
        mat = self.re.match(msg)
        if not mat:
            return "格式：/transfer [id] @某人"

        pot_id = int(mat.group(1))
        transfer_to = int(mat.group(2))

        with Session(engine) as session:
            target = session.query(PotDB).filter(PotDB.id == pot_id, PotDB.expire_time > now_plus_8()).first()

            if not target:
                return "锅不存在"

            if target.creator["user_id"] != member.user_id:
                return "只有发起人可以转让发起人"

            # 查找被转让人在成员列表中的信息
            target_member = next(
                (m for m in target.members if m["user_id"] == transfer_to),
                None,
            )

            if target_member is None:
                return "被转让者不在锅中，无法转让"

            target.creator = target_member
            session.add(target)
            session.commit()

        return f"已将 {pot_id} 的发起人转让给 {target_member['nickname']}"


CommandRegistry.register(TransferCommand)
