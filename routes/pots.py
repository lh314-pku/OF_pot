from sqlalchemy.orm import Session
from routes.base import BaseCommand, CommandRegistry
from db import engine
from models import PotDB, CTX, now_plus_8

import re
import datetime

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
            return "\n===========\n".join(map(self._get_detail, pots))
    
    def _get_detail(self, pot: PotDB):
        expire_str = pot.expire_time.strftime("%Y-%m-%d %H:%M:%S")
        return f"ID: {pot.id}\n内容: {pot.detail}\n发起人: {pot.creator['nickname']}\n成员: {', '.join([m['nickname'] for m in pot.members])}\n过期时间: {expire_str}"

CommandRegistry.register(PotsCommand)