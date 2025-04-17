import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application

from .handlers.handler import setup_handlers
from .manager import setup_manager

class Bot:
    def __init__(self, app: "Application"):
        self.app = app

        from .router import Router
        from .states.state_manager import FSM
        from .states.models import BotStates
        
        self.router = Router()
        self.fsm = FSM()
        self.states = BotStates()
        
        
def setup_bot(app: "Application") -> None:
    app.bot = Bot(app)
    setup_handlers(app)
    setup_manager(app)
