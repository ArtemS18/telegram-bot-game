import typing
from .asyncio import AsyncioUtils

if typing.TYPE_CHECKING:
    from app.web.app import Application

class Utils:
    def __init__(self, app: "Application"):
        self.asyncio = AsyncioUtils(app)

def setup_utils(app: "Application"):
    app.bot.utils = Utils(app)
