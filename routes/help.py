from routes.base import BaseCommand, CommandRegistry
from routes.registry import get_help_text

from models import CTX

class HelpCommand(BaseCommand):
    name = "/help"
    help = "显示帮助"

    async def handle(self, ctx: CTX):
        return get_help_text()


CommandRegistry.register(HelpCommand)