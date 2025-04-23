from typing import List, Optional
from pydantic import BaseModel


class QuestionCreateRequest(BaseModel):
    question_text: str
    answer_text: str
    img_url: Optional[str] = None


class QuestionUpdateRequest(BaseModel):
    question_text: Optional[str] = None
    answer_text: Optional[str] = None
    img_url: Optional[str] = None


class QuestionResponse(BaseModel):
    id: int
    question_text: str
    answer_text: str
    img_url: Optional[str] = None

    class Config:
        orm_mode = True

class QuestionsResponse(BaseModel):
    questions: List[QuestionResponse]