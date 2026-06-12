from sqlalchemy.orm import Session
from routes.base import BaseCommand, CommandRegistry
from db import engine
from models import PotDB, CTX

import re

class DeleteCommand(BaseCommand):
    name = "/delete"
    help = "删除锅"
    pattern = "/delete [id]"
    re = re.compile(r"^/delete\s+(\d+)$")

    async def handle(self, ctx: CTX):
        msg = ctx.msg

        mat = self.re.match(msg)
        if not mat:
            return "格式：/delete 1"

        pot_id = int(mat.group(1))

        with Session(engine) as session:
            target = session.get(PotDB, pot_id)

            if not target:
                return "锅不存在"

            session.delete(target)
            session.commit()

        return f"已删除 {pot_id}"


CommandRegistry.register(DeleteCommand)