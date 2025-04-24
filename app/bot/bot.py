import asyncio
import typing
from collections import defaultdict

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

        from .router import Router
        from .states.models import BotState

        self.router = Router()
        self.states = BotState()
        self.answer_queues = defaultdict(asyncio.Queue)


def setup_bot(app: "Application") -> None:
    app.bot = Bot(app)
    setup_fsm(app)
    setup_utils(app)
    setup_handlers(app)
    setup_middleware(app)
    setup_manager(app)
