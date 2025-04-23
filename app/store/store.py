import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        self.app = app

        from app.store.database.accessor import DatabaseAccessor
        from app.store.game.accessor import GameAccessor
        from app.store.tg_api.accessor import TgApiAccessor
        from app.store.question.accessor import QuestionAccessor

        self.tg_api = TgApiAccessor(app)
        self.database = DatabaseAccessor(app)
        self.game = GameAccessor(app)
        self.question = QuestionAccessor(app)


def setup_store(app: "Application") -> None:
    app.store = Store(app)
