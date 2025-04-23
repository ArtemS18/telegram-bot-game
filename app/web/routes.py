from aiohttp.web_app import Application
from app.question.routes import setup_routes as setup_question_routes
from app.admin.routes import setup_admin_routes

def setup_routes(app: Application):
    setup_admin_routes(app)
    setup_question_routes(app)
