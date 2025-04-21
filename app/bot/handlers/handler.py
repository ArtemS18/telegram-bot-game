import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Handler:
    def __init__(self, app: "Application"):
        self.app = app

        from .callback_handler import CallbackHandler
        from .command_handler import CommandHandler
        from .game_handler import GameHandler

        self.command = CommandHandler(app)
        self.callback = CallbackHandler(app)
        self.game = GameHandler(app)


def setup_handlers(app: "Application") -> None:
    app.bot.handlers = Handler(app)
