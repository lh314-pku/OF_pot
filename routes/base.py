from typing import Callable, Dict, Optional, Type

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
    detail: Optional[str] = None
    pattern: Optional[str] = None
    re: Optional[Pattern] = None

    async def handle(self, ctx: CTX):
        raise NotImplementedError