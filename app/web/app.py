from fastapi import FastAPI as FastApiApplication

from app.bot.bot import setup_bot
from app.store.store import setup_store

from .config import setup_config, setup_etc_config
from .logger import setup_logging
from .routes import setup_routes

__all__ = ("Application",)


class Application(FastApiApplication):
    config = None
    store = None
    database = None
    router = None
    log = None
    bot = None


app = Application()
    


def setup_app(config_path: str, etc_config_path: str) -> Application:
    setup_config(app, config_path)
    setup_etc_config(app, etc_config_path)
    setup_logging(app)
    setup_routes(app)
    setup_store(app)
    setup_bot(app)
    return app
