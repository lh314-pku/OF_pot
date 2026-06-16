from sqlalchemy.orm import Session
from routes.base import BaseCommand, CommandRegistry
from db import engine
from models import PotDB, CTX, now_plus_8

import re

class JoinCommand(BaseCommand):
    name = "/join"
    help = "加入锅"
    pattern = "/join [id]"
    detail = "通过 ID 加入一个未过期的锅。已在锅中则自动更新昵称。"
    re = re.compile(r"^/join\s+(\d+)$")

    async def handle(self, ctx: CTX):
        msg = ctx.msg
        member = ctx.member

        assert self.re is not None
        mat = self.re.match(msg)
        if not mat:
            return "格式：/join 1"

        pot_id = int(mat.group(1))

        with Session(engine) as session:
            target = session.query(PotDB).filter(PotDB.id == pot_id, PotDB.expire_time > now_plus_8()).first()

            if not target:
                return "锅不存在"

            members = list(target.members) # list[{"nickname": xxx, "user_id": xxx}]
            if member.user_id not in [m["user_id"] for m in members]:
                members.append({"nickname": member.nickname, "user_id": member.user_id})
                target.members = members
                session.commit()
            else:
                # nickname 软更新
                for m in members:
                    if m["user_id"] == member.user_id:
                        if m["nickname"] != member.nickname:
                            m["nickname"] = member.nickname
                            target.members = members
                            session.commit()

        return f"已加入 {pot_id}"


CommandRegistry.register(JoinCommand)