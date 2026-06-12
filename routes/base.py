from typing import Callable, Dict, Type

from models import CTX

from re import Pattern

class CommandRegistry:
    commands: Dict[str, "BaseCommand"] = {}

    @classmethod
    def register(cls, cmd_cls: Type["BaseCommand"]):
        instance = cmd_cls()
        cls.commands[instance.name] = instance


class BaseCommand:
    name: str = ""
    help: str = ""
    pattern: str | None = None
    re: Pattern = None

    async def handle(self, ctx: CTX):
        raise NotImplementedError