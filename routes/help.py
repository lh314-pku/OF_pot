from routes.base import BaseCommand, CommandRegistry
from routes.registry import get_help_text

from models import CTX

class HelpCommand(BaseCommand):
    name = "/help"
    help = "显示帮助"
    detail = "显示所有命令列表及基本用法。使用 /detail [命令] 查看具体命令的详细说明。"

    async def handle(self, ctx: CTX):
        return get_help_text()


CommandRegistry.register(HelpCommand)