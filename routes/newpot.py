from sqlalchemy.orm import Session
from routes.base import BaseCommand, CommandRegistry
from db import engine
from models import PotDB, CTX

import re

class NewPotCommand(BaseCommand):
    name = "/newpot"
    help = "创建锅"
    pattern = "/newpot [内容]"
    re = re.compile(r"^/newpot\s+(.+)$")

    async def handle(self, ctx: CTX):
        msg = ctx.msg
        member = ctx.member

        mat = self.re.match(msg)
        if not mat:
            return "格式：/newpot 内容"
        
        detail = mat.group(1)

        with Session(engine) as session:
            pot = PotDB(
                creator=member.to_dict(),
                detail=detail,
                members=[member.to_dict()]
            )
            session.add(pot)
            session.commit()
            session.refresh(pot)

        return f"创建成功 ID:{pot.id}"

CommandRegistry.register(NewPotCommand)