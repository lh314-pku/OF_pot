from sqlalchemy.orm import Session
from routes.base import BaseCommand, CommandRegistry
from db import engine
from models import PotDB, CTX, now_plus_8

import re

class EditCommand(BaseCommand):
    name = "/edit"
    pattern = "/edit [id] [内容]"
    help = "修改锅的描述（仅限发起人）"
    detail = "修改锅的描述内容。仅发起人可操作。"
    re = re.compile(r"^/edit\s+(\d+)\s+(.+)$")

    async def handle(self, ctx: CTX):
        msg = ctx.msg
        member = ctx.member

        assert self.re is not None
        mat = self.re.match(msg)
        if not mat:
            return "格式：/edit [id] [新内容]"

        pot_id = int(mat.group(1))
        new_detail = mat.group(2)

        with Session(engine) as session:
            target = session.query(PotDB).filter(PotDB.id == pot_id, PotDB.expire_time > now_plus_8()).first()

            if not target:
                return "锅不存在"

            if target.creator["user_id"] != member.user_id:
                return "只有发起人可以修改锅的描述"

            target.detail = new_detail
            session.add(target)
            session.commit()

        return f"已修改 {pot_id} 的描述"


CommandRegistry.register(EditCommand)
