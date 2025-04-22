import logging
from collections import defaultdict
from collections.abc import Callable

from .states.models import State


class Router:
    def __init__(self):
        self.handlers = defaultdict(lambda: defaultdict(dict))

    def register(
            self, command: str | None = None, 
            state: State = State()
            ):
        def decorator(handler: Callable):
            self.handlers["message"][state.name][command] = handler
            return handler

        return decorator

    def callback_register(self, data: str | None = None, state: State = State()):
        def decorator(handler: Callable):
            self.handlers["callback_query"][state.name][data] = handler
            return handler

        return decorator

    async def handle(
                self,
                command_type: str,
                command: str | None = None,
                state: State = State(),
                *args,
                **kwargs
                    ):
        handler = self.handlers.get(command_type, {}).get(state.name, {}).get(command)
        logging.info("Команда: %s, Состояние: %s", command, state.name)
        if handler:
            return await handler(*args, **kwargs)
        logging.info(
            "Команда '%s' '%s' и '%s' не зарегистрированы.",
            command_type,
            command,
            state.name,
        )
        return None
