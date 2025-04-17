import typing


if typing.TYPE_CHECKING:
    from app.web.app import Application

class Handler:
     def __init__(self, app: "Application"):
        self.app = app

        from .command_handler import CommandHandler
        from .callback_handler import CallbackHandler

        self.command = CommandHandler(app)
        self.callback = CallbackHandler(app)
        
def setup_handlers(app: "Application") -> None:
    app.bot.handlers = Handler(app)