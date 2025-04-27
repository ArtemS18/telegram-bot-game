from typing import List
from sqlalchemy import insert, select, update, delete

from app.base.base_sqlalchemy import BaseModel
from app.game.models.play import Chat, Question
from app.base.base_accessor import BaseAccessor
from app.bot.states.models import BotState


class SateAccessor(BaseAccessor):
    async def get_state_by_chat_id(self, chat_id: int) -> BotState | None:
        query = select(Chat.bot_state).where(Chat.id == chat_id).limit(1)
        async with self.app.store.database.session() as session:
            res = await session.execute(query)
            value = res.scalar_one_or_none()
            print("get", value)
            return value if value else BotState("NONE")
        
    async def set_state_by_chat_id(
        self, 
        chat_id: int, 
        state: BotState
    ) -> BotState | None:
        update_query = (
            update(Chat)
            .values(bot_state=state.name)
            .where(Chat.id == chat_id)
            .returning(Chat.bot_state)
        )
        print("set", state.name)
        async with self.app.store.database.session() as session:
            res = await session.execute(update_query)
            await session.commit()
            raw_value = res.scalar_one_or_none()
            return raw_value if raw_value else  BotState("NONE")