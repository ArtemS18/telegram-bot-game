from typing import List
from sqlalchemy import insert, select, update, delete

from app.base.base_sqlalchemy import BaseModel
from app.game.models.play import Question
from app.base.base_accessor import BaseAccessor


class QuestionAccessor(BaseAccessor):
    async def create_question(
        self,
        question_text: str,
        answer_text: str,
        img_url: str | None = None
    ) -> Question:
        query = insert(Question).values(
            question_text=question_text,
            answer_text=answer_text,
            img_url=img_url
        ).returning(Question)

        async with self.app.store.database.session() as session:
            res = await session.execute(query)
            await session.commit()
            return res.scalar_one()

    async def get_question_by_id(self, question_id: int) -> Question | None:
        query = select(Question).where(Question.id == question_id)
        async with self.app.store.database.session() as session:
            res = await session.execute(query)
            return res.scalar_one_or_none()

    async def update_question(
        self,
        question_id: int,
        question_text: str | None = None,
        answer_text: str | None = None,
        img_url: str | None = None
    ) -> Question | None:
        fields = {
            key: value for key, value in {
                "question_text": question_text,
                "answer_text": answer_text,
                "img_url": img_url
            }.items() if value is not None
        }

        if not fields:
            return None

        query = (
            update(Question)
            .where(Question.id == question_id)
            .values(**fields)
            .returning(Question)
        )

        async with self.app.store.database.session() as session:
            res = await session.execute(query)
            await session.commit()
            return res.scalar_one_or_none()
        
    async def get_all_questions(self) -> List[Question]:
        query = select(Question)
        async with self.app.store.database.session() as session:
            res = await session.execute(query)
            await session.commit()
            return res.scalars().all()

    async def delete_question(self, question_id: int) -> bool:
        query = delete(Question).where(Question.id == question_id)
        async with self.app.store.database.session() as session:
            await session.execute(query)
            await session.commit()
            return True