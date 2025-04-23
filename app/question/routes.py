import typing
from app.question.view import QuestionView
if typing.TYPE_CHECKING:
    from app.web.app import Application

def setup_routes(app: "Application"):
    question_view = QuestionView(app)
    app.include_router(question_view.get_router())