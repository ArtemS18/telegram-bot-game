from typing import List
from sqlalchemy import insert, select, update, delete

from app.base.base_sqlalchemy import BaseModel
from app.game.models.play import Chat, Question
from app.base.base_accessor import BaseAccessor
from app.bot.states.models import BotState


class SateAccessor(BaseAccessor):
    async def get_state_by_chat_id(self, chat_id: int) ->  BotState | None:
        state = select(Chat.bot_state).where(Chat.id == chat_id).limit(1)
        async with self.app.store.database.session() as session:
            res = await session.execute(state)
            return res.scalar_one_or_none()
        
    async def set_state_by_chat_id(
            self, 
            chat_id: int, 
            state : BotState
        ) -> BotState | None:
        update_query = (update(Chat)
                        .values(bot_state=state)
                        .where(Chat.id == chat_id)
                        .returning(BotState))
        async with self.app.store.database.session() as session:
            res = await session.execute(state)
            return res.scalar_one_or_none()