import asyncio
import logging
from collections import defaultdict
from collections.abc import Callable
import typing

from .states.models import BotState

if typing.TYPE_CHECKING:
    from app.web.app import Application




class Router:
    def __init__(self, app: "Application"):
        self.app = app
        self.handlers = defaultdict(lambda: defaultdict(dict))
        self.on_startup_handlers = defaultdict(dict)
        self.active_tasks = app.bot.active_tasks

    def startup_register(
            self,
            state: BotState = BotState.none
            ):
        def decorator(handler: Callable):
            self.on_startup_handlers["message"][state.name] = handler
            return handler

        return decorator
    
    async def on_startup_handle(
                self,
                state: BotState = BotState.none,
                *args, **kwargs
        ):
        obj = kwargs.get("callback") or kwargs.get("message")
        if not obj:
            return
        chat_id = (
            getattr(getattr(obj, "message", obj), "chat", None).id
            if hasattr(obj, "message")
            else obj.chat.id
        )
        handler = self.on_startup_handlers.get("message", {}).get(state.name)
        logging.info(" Состояние: %s", state.name)
        if handler:
            logging.info("Запуск начальной функции %s", str(handler))
            task=asyncio.create_task(handler(*args, **kwargs))
            if not self.app.bot.active_tasks.get(chat_id):
                self.app.bot.active_tasks[chat_id] = []
            self.active_tasks[chat_id].append(task)
            task.add_done_callback(lambda t: self.active_tasks.pop(chat_id, None))
        return None

    def register(
            self,
            command: str | None = None, 
            state: BotState = BotState.none
            ):
        def decorator(handler: Callable):
            self.handlers["message"][state.name][command] = handler
            return handler

        return decorator

    def callback_register(self, data: str | None = None, state: BotState = BotState.none):
        def decorator(handler: Callable):
            self.handlers["callback_query"][state.name][data] = handler
            return handler

        return decorator

    async def handle(
                self,
                command_type: str,
                command: str | None = None,
                state: BotState = BotState.none,
                *args, **kwargs
        ):
        handler = self.handlers.get(command_type, {}).get(state.name, {}).get(command)
        logging.info("Команда: %s, Состояние: %s", command, state.name)
        obj = args[0]
        chat_id = (
            getattr(getattr(obj, "message", obj), "chat", None).id
            if hasattr(obj, "message")
            else obj.chat.id
        )
        if handler and state.name == "creation_game":
            task=asyncio.create_task(handler(*args, **kwargs))
            if not self.app.bot.active_tasks.get(chat_id):
                self.app.bot.active_tasks[chat_id] = []
            self.active_tasks[chat_id].append(task)
            task.add_done_callback(lambda t: self.active_tasks.pop(chat_id, None))
            return

        if handler:
            return await handler(*args, **kwargs)
        handler = self.handlers.get(command_type, {}).get(state.name, {}).get(None)
        if handler:
            return await handler(*args, **kwargs)
        logging.info(
            "Команда '%s' '%s' и '%s' не зарегистрированы.",
            command_type,
            command,
            state.name,
        )
       
        return None

def setup_router(app: "Application"):
    app.bot.router = Router(app)