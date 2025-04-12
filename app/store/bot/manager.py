import typing

from app.store.tg_api.models import (
    Update,
)

from .command_hendler import CommandHandler
from .dispatcher import CommandDispatcher

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.dispatcher = CommandDispatcher()
        self.comand_handler = CommandHandler(app)
        self._register_commands()

    def _register_commands(self):
        self.dispatcher.register_command(
            "/start", self.comand_handler.start_command
            )
        self.dispatcher.register_command(
            "/add", self.comand_handler.add_user
            )
        
    async def handle_updates(self, updates: list[Update]):
        """Обрабатывает список обновлений, полученных от TG API."""
        for update in updates:
            if update.message.text:
                message = update.message
                if message.text.strip():
                    await self.dispatcher.handle_command(message.text, message)
                    # await self.app.store.tg_api.send_message(message)
