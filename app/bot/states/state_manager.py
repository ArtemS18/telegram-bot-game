import logging
import typing

from .models import BotState

if typing.TYPE_CHECKING:
    from app.web.app import Application
    from app.store.state.accessor import SateAccessor

class FSM:
    def __init__(self, app: "Application"):
        self.db: "SateAccessor" = app.store.state

    def get_state(self, chat_id) -> BotState:
        return self.db.get_state_by_chat_id(chat_id)

    def set_state(self, chat_id, state: BotState):
        return self.db.set_state_by_chat_id(chat_id)

def setup_fsm(app: "Application"):
    app.bot.fsm = FSM(app)
