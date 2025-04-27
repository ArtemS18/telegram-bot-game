import typing

from .auth import AuthMiddleware

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Middleware:
    def __init__(self, app: "Application"):
        self.auth = AuthMiddleware(app)


def setup_middleware(app: "Application"):
    app.bot.middleware = Middleware(app)
