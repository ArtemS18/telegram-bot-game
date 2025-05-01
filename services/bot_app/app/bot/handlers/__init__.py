import typing

from .callback import CallbackHandler
from .command import CommandHandler
from .game import GameHandler

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Handler:
    def __init__(self, app: "Application"):
        self.app = app
        self.command = CommandHandler(app)
        self.callback = CallbackHandler(app)
        self.game = GameHandler(app)


def setup_handlers(app: "Application") -> None:
    app.bot.handlers = Handler(app)
