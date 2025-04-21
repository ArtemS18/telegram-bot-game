import asyncio
import typing
from collections import defaultdict

if typing.TYPE_CHECKING:
    from app.web.app import Application

from .handlers.handler import setup_handlers
from .manager import setup_manager
from .middleware import setup_middleware


class Bot:
    def __init__(self, app: "Application"):
        self.app = app

        from .router import Router
        from .states.models import BotStates
        from .states.state_manager import FSM

        self.router = Router()
        self.fsm = FSM()
        self.states = BotStates()
        self.answer_queues = defaultdict(asyncio.Queue)


def setup_bot(app: "Application") -> None:
    app.bot = Bot(app)
    setup_handlers(app)
    setup_middleware(app)
    setup_manager(app)
