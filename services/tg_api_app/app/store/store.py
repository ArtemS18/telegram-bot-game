import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        self.app = app

        from .tg_api.accessor import TgApiAccessor

        self.tg_api = TgApiAccessor(app)

def setup_store(app: "Application") -> None:
    app.store = Store(app)
