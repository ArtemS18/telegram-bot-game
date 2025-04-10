import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        self.app = app

        from app.store.bot.manager import BotManager
        from app.store.tg_api.accessor import TgApiAccessor

        self.tg_api = TgApiAccessor(app)
        self.bot_manager = BotManager(app)


def setup_store(app: "Application") -> None:
    app.store = Store(app)