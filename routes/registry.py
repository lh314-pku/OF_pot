from routes.base import CommandRegistry
from models import CTX

async def dispatch_command(name: str, ctx: CTX):
    cmd = CommandRegistry.commands.get(name)

    if not cmd:
        return None

    return await cmd.handle(ctx)


def get_help_text():
    lines = ["约锅Bot\n"]

    for cmd in CommandRegistry.commands.values():
        lines.append(f"{cmd.pattern or cmd.name} : {cmd.help}")

    return "\n\n".join(lines)