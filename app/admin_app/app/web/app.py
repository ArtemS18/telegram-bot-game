from fastapi import FastAPI as FastApiApplication


from app.web.logger import setup_logging
from app.store.store import setup_store

from .config import setup_config, setup_etc_config

from ..admin.routes import setup_admin_routes
from ..question.routes import setup_question_routes

__all__ = ("Application",)


class Application(FastApiApplication):
    config = None
    store = None
    router = None
    log = None


app = Application()
    


def setup_app(config_path: str, etc_config_path: str) -> Application:
    setup_logging(app)
    setup_config(app, config_path)
    setup_etc_config(app, etc_config_path)
    setup_admin_routes(app)
    setup_question_routes(app)
    setup_store(app)
    return app