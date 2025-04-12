import logging
from collections.abc import Callable


class CommandDispatcher:
    def __init__(self):
        self.commands: dict[str, Callable] = {}

    def register_command(self, command: str, handler: Callable):
        self.commands[command] = handler

    async def handle_command(self, command: str, *args, **kwargs):
        handler = self.commands.get(command)
        if handler:
            return await handler(*args, **kwargs)
        logging.info("Команда '%s' не зарегистрирована.", command)
        return None