from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from app.web.app import get_app
from app.game.models.play import Question

router = APIRouter(prefix="/admin/questions", tags=["Admin Questions"])

class QuestionCreateRequest(BaseModel):
    question_text: str
    answer_text: str
    img_url: Optional[str] = None


class QuestionUpdateRequest(BaseModel):
    question_text: Optional[str] = None
    answer_text: Optional[str] = None
    img_url: Optional[str] = None
    
@router.post("/", response_model=Question)
async def create_question(data: QuestionCreateRequest, app=Depends(get_app)):
    accessor = app.store.question_accessor
    return await accessor.create_question(
        question_text=data.question_text,
        answer_text=data.answer_text,
        img_url=data.img_url
    )


@router.get("/{question_id}", response_model=Question)
async def get_question(question_id: int, app=Depends(get_app)):
    accessor = app.store.question_accessor
    question = await accessor.get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.put("/{question_id}", response_model=Question)
async def update_question(
    question_id: int,
    data: QuestionUpdateRequest,
    app=Depends(get_app)
):
    accessor = app.store.question_accessor
    updated = await accessor.update_question(
        question_id,
        question_text=data.question_text,
        answer_text=data.answer_text,
        img_url=data.img_url
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Question not found or no fields to update")
    return updated


@router.delete("/{question_id}")
async def delete_question(question_id: int, app=Depends(get_app)):
    accessor = app.store.question_accessor
    success = await accessor.delete_question(question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"status": "deleted"}