import asyncio
import typing
from collections import defaultdict

from app.bot.router import setup_router

if typing.TYPE_CHECKING:
    from app.web.app import Application

from .handlers import setup_handlers
from .manager import setup_manager
from .middleware import setup_middleware
from .utils import setup_utils
from .states.state_manager import setup_fsm


class Bot:
    def __init__(self, app: "Application"):
        self.app = app

        
        from .states.models import BotState
        self.states = BotState.none
        self.active_tasks: dict[int, typing.List[asyncio.Task]] = {}
        self.answer_queues = defaultdict(asyncio.Queue)


def setup_bot(app: "Application") -> None:
    app.bot = Bot(app)
    setup_fsm(app)
    setup_router(app)
    setup_utils(app)
    setup_handlers(app)
    setup_middleware(app)
    setup_manager(app)
