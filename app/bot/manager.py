import typing

from app.store.tg_api.models import (
    Update,
)

from .command_hendler import CommandHandler
from .router import Router
from .models.state_manager import FSM, State

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.router = Router()
        self.fsm = FSM()
        self._register_routes()

    def _register_routes(self):
        handler = CommandHandler(self.app)
        self.router.register(command="/start")(handler.start_command)
        self.router.register(command="/join", state=State("START"))(handler.add_user)

        self.router.callback_register(data = "start_game", state=State("START"))(handler.query)

    async def handle_updates(self, updates: list[Update]):
        """Обрабатывает список обновлений, полученных от TG API."""
        for update in updates:
            if update.type_query == "message":
                command = update.message.text.strip()
                chat_id = update.message.chat.id
                args = (update.message,)
            elif update.type_query == "callback_query":
                command = update.callback_query.data
                chat_id = update.callback_query.message.chat.id
                args = (update.callback_query,)
            else:
                continue

            current_state = self.fsm.get_state(chat_id)

            await self.router.handle(update.type_query, command, current_state, *args)
