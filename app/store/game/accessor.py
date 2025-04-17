import typing

from sqlalchemy  import insert, select

from app.base.base_accessor import BaseAccessor
from sqlalchemy.ext.asyncio import AsyncEngine
from app.base.base_sqlalchemy import BaseModel

from app.game.models.play import (
    Game,
    Question,
    GameUser,
    User,
    Chat,
)

if typing.TYPE_CHECKING:
    from aiohttp.web import Application


class GameAccessor(BaseAccessor):

    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
    
    async def create_tables(self):
        async with self.app.store.database.engine.begin() as conn:
            
            await conn.run_sync(BaseModel.metadata.create_all)
            self.app.log.info("Create TABLES")

    async def create_user(self, id: int) -> User:
        insert_request = insert(User).values(id=id)
        async with self.app.store.database.session() as session:
            await session.execute(insert_request)
            await session.commit()
            return await self.get_user_by_id(id)
        
    async def get_user_by_id(self, id: int) -> User | None:
        select_request = select(User).where(User.id == id)
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            try:
                new_res = res.scalars().one()
                return User(
                    id=new_res.id, 
                    count_wins=new_res.count_wins,
                    count_losses=new_res.count_losses,
                    is_admin=new_res.is_admin
                    )
            except Exception:
                return None
        
    async def create_chat(self, id: int) -> Chat:
        insert_request = insert(Chat).values(id=id)
        async with self.app.store.database.session() as session:
            await session.execute(insert_request)
            await session.commit()
            return await self.get_chat_by_id(id)

    async def create_game(self, id: int) -> Game:
        insert_request = insert(Game).values(id=id)
        async with self.app.store.database.session() as session:
            await session.execute(insert_request)
            await session.commit()
            return await self.get_game_by_id(id)
        

