from aiohttp.web import Application as AioApplication

from app.bot.bot import setup_bot
from app.store.store import setup_store

from .config import setup_config
from .logger import setup_logging


__all__ = ("Application",)


class Application(AioApplication):
    config = None
    store = None
    database = None
    log = None
    bot = None


app = Application()
    


def setup_app(config_path: str) -> Application:
    setup_config(app, config_path)
    setup_logging(app)
    setup_store(app)
    setup_bot(app)
    return app
