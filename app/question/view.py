from fastapi import APIRouter, Depends, HTTPException
from app.question.schemes import QuestionCreateRequest, QuestionUpdateRequest, QuestionResponse, QuestionsResponse
from app.web.mx import AdminAuth

class QuestionView:
    def __init__(self, app):
        self.app = app
        self.mx = AdminAuth(app)
        self.router = APIRouter(
            prefix="/admin/questions", 
            tags=["Admin Questions"],
            dependencies=[Depends(self.mx.get_current_admin)])
        self.router.add_api_route(
            "/", self.create_question, 
            methods=["POST"], response_model=QuestionResponse
        )
        self.router.add_api_route(
            "/", self.get_questions, 
            methods=["GET"], response_model=QuestionsResponse
        )
        self.router.add_api_route(
            "/{question_id}", self.get_question,
            methods=["GET"], response_model=QuestionResponse
        )
        self.router.add_api_route(
            "/{question_id}", self.update_question, 
            methods=["PUT"], response_model=QuestionResponse
        )
        self.router.add_api_route(
            "/{question_id}", self.delete_question, 
            methods=["DELETE"]
        )

    async def create_question(self, data: QuestionCreateRequest):
        accessor = self.app.store.question
        return await accessor.create_question(
            question_text=data.question_text,
            answer_text=data.answer_text,
            img_url=data.img_url
        )

    async def get_question(self, question_id: int):
        accessor = self.app.store.question
        question = await accessor.get_question_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        return question
    
    async def get_questions(self):
        accessor = self.app.store.question
        questions = await accessor.get_all_questions()
        if not questions:
            raise HTTPException(status_code=404, detail="Questions not found")
        return {"questions": questions}

    async def update_question(self, question_id: int, data: QuestionUpdateRequest):
        accessor = self.app.store.question
        updated = await accessor.update_question(
            question_id,
            question_text=data.question_text,
            answer_text=data.answer_text,
            img_url=data.img_url
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Question not found or no fields to update")
        return updated

    async def delete_question(self, question_id: int):
        accessor = self.app.store.question
        success = await accessor.delete_question(question_id)
        if not success:
            raise HTTPException(status_code=404, detail="Question not found")
        return {"status": "deleted"}

    def get_router(self):
        return self.router