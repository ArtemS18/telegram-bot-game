import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        self.app = app

        from .database.accessor import DatabaseAccessor
        from .question.accessor import QuestionAccessor

        self.database = DatabaseAccessor(app)
        self.question = QuestionAccessor(app)


def setup_store(app: "Application") -> None:
    app.store = Store(app)
