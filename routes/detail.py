from routes.base import BaseCommand, CommandRegistry
from models import CTX

import re


class DetailCommand(BaseCommand):
    name = "/detail"
    help = "查看命令详细用法"
    pattern = "/detail [命令]"
    detail = "用法：/detail <命令名>\n示例：/detail /settime"
    re = re.compile(r"^/detail\s+(.+)$")

    async def handle(self, ctx: CTX):
        msg = ctx.msg

        assert self.re is not None
        mat = self.re.match(msg)
        if not mat:
            return "格式：/detail [命令名]\n示例：/detail /settime"

        cmd_name = mat.group(1).strip()
        cmd = CommandRegistry.commands.get(cmd_name)

        if not cmd:
            return f"未知命令：{cmd_name}"

        if cmd.detail:
            return f"{cmd.name}\n用法：{cmd.pattern or cmd.name}\n\n{cmd.detail}"
        else:
            return f"{cmd.name}\n{cmd.help}\n\n该命令暂无详细说明"


CommandRegistry.register(DetailCommand)
