from aiohttp.web import Application as AiohhtpApplication

from app.store.store import setup_store

from .config import setup_config
from .logger import setup_logging

__all__ = ("Application",)


class Application(AiohhtpApplication):
    config = None
    store = None
    router = None
    log = None


app = Application()
    


def setup_app(config_path: str) -> Application:
    setup_config(app, config_path)
    setup_logging(app)
    setup_store(app)
    return app
