from sqlalchemy.orm import Session
from routes.base import BaseCommand, CommandRegistry
from db import engine
from models import PotDB, CTX

import re

# at的纯文本表现为：[CQ:at,qq=3793626092]

class RemoveCommand(BaseCommand):
    name = "/remove"
    pattern = "/remove [id] (at某人)"
    help = "从锅中删除自己（发起者可删除任意人）"
    re = re.compile(r"^/remove\s+(\d+)(?:\s*\[CQ:at,qq=(\d+)\])?$")

    async def handle(self, ctx: CTX):
        msg = ctx.msg
        member = ctx.member

        mat = self.re.match(msg)
        if not mat:
            return "格式：/delete 1 （删除自己）或 /delete 1 at某人 （删除某人）"

        pot_id = int(mat.group(1))
        remove_id = int(mat.group(2)) if mat.group(2) else None

        with Session(engine) as session:
            target = session.get(PotDB, pot_id)

            if not target:
                return "锅不存在"

            if remove_id is None or remove_id == member.user_id:
                # 删除自己
                target.members = [m for m in target.members if m["user_id"] != member.user_id]
                
                # 特殊判断，发起人离开后随机指定一个新发起人
                # 注意：如果锅里没人了，直接删除锅
                if not target.members:
                    session.delete(target)
                elif target.creator["user_id"] == member.user_id:
                    target.creator = target.members[0]
                    session.add(target)
                    
                session.commit()
                return f"已从 {pot_id} 离开" + (f"，新发起人是 {target.creator['nickname']}" if target.members and target.creator["user_id"] != member.user_id else "")
            else:
                # 删除其他人
                # 只有发起人可以删除其他人
                if target.creator["user_id"] != member.user_id:
                    return "只有发起人可以删除其他人"
                
                # 如果要删除的人不在锅里
                member_list = [m["user_id"] for m in target.members]
                if remove_id not in member_list:
                    return "要删除的人不在锅里"
                
                # 删除指定的人
                target.members = [m for m in target.members if m["user_id"] != remove_id]
                session.add(target)
                session.commit()
                
                return f"已将 {remove_id} 从 {pot_id} 中删除"

CommandRegistry.register(RemoveCommand)