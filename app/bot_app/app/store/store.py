import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        self.app = app

        from app.store.database.accessor import DatabaseAccessor
        from app.store.game.accessor import GameAccessor
        from app.store.tg_api.accessor import TgApiAccessor
        from app.store.state.accessor import SateAccessor

        self.tg_api = TgApiAccessor(app)
        self.database = DatabaseAccessor(app)
        self.game = GameAccessor(app)
        self.state = SateAccessor(app)


def setup_store(app: "Application") -> None:
    app.store = Store(app)
