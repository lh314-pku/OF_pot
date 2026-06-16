from sqlalchemy.orm import Session
from routes.base import BaseCommand, CommandRegistry
from db import engine
from models import PotDB, CTX, now_plus_8

import re

class DeleteCommand(BaseCommand):
    name = "/delete"
    help = "删除锅"
    pattern = "/delete [id]"
    detail = "删除指定 ID 的锅。注意：此操作不可恢复。"
    re = re.compile(r"^/delete\s+(\d+)$")

    async def handle(self, ctx: CTX):
        msg = ctx.msg

        assert self.re is not None
        mat = self.re.match(msg)
        if not mat:
            return "格式：/delete 1"

        pot_id = int(mat.group(1))

        with Session(engine) as session:
            target = session.query(PotDB).filter(PotDB.id == pot_id, PotDB.expire_time > now_plus_8()).first()

            if not target:
                return "锅不存在"

            session.delete(target)
            session.commit()

        return f"已删除 {pot_id}"


CommandRegistry.register(DeleteCommand)