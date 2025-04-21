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
        
    async def create_chat(self, id: int) -> Chat:
        insert_request = insert(Chat).values(id=id)
        async with self.app.store.database.session() as session:
            await session.execute(insert_request)
            await session.commit()
            return await self.get_chat_by_id(id)

    async def create_game(self, chat_id: int) -> Game:
        insert_request = insert(Game).values(chat_id=chat_id)
        async with self.app.store.database.session() as session:
            await session.execute(insert_request)
            await session.commit()
            return await self.get_game_by_chat_id(chat_id)
        
    async def create_gameuser(self, game_id: int, user_id:int) -> GameUser:
        insert_request = insert(GameUser).values(game_id=game_id, user_id=user_id)
        async with self.app.store.database.session() as session:
            await session.execute(insert_request)
            await session.commit()
            return await self.get_game_by_id(id)
        
    async def get_chat_by_id(self, id: int) -> User | None:
        select_request = select(Chat).where(Chat.id == id)
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            try:
                new_res = res.scalars().one()
                return Chat(
                    id=new_res.id, 
                    bot_state=new_res.bot_state
                    )
            except Exception:
                return None
    
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
            
    async def get_gameuser_by_id(self, id: int) -> GameUser | None:
        select_request = select(GameUser).where(GameUser.id == id)
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            try:
                new_res = res.scalars().one()
                return GameUser(
                    id=new_res.id, 
                    user_id=new_res.user_id,
                    game_id=new_res.game_id,
                    game_role=new_res.game_role
                    )
            except Exception:
                return None
            
    async def get_gameuser_by_user_and_game(self, game_id: int, user_id:int) -> GameUser | None:
        select_request = select(GameUser).where(GameUser.game_id == game_id and GameUser.user_id == user_id)
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            try:
                new_res = res.scalars().one()
                return GameUser(
                    id=new_res.id, 
                    user_id=new_res.user_id,
                    game_id=new_res.game_id,
                    game_role=new_res.game_role
                    )
            except Exception:
                return None
            

    async def get_game_by_id(self, id: int) -> Game | None:
        select_request = select(Game).where(Game.id == id)
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            try:
                new_res = res.scalars().one()
                return Game(
                    id=new_res.id,
                    chat_id=new_res.chat_id,
                    score_gamers=new_res.score_gamers,
                    score_bot=new_res.score_bot,
                    round=new_res.round,
                    status=new_res.status,
                    winner=new_res.winner
                )
            except Exception:
                return None

    async def get_game_by_chat_id(self, chat_id: int) -> Game | None:
        select_request = select(Game).where(Game.chat_id == chat_id)
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            try:
                new_res = res.scalars().one()
                return Game(
                    id=new_res.id,
                    chat_id=new_res.chat_id,
                    score_gamers=new_res.score_gamers,
                    score_bot=new_res.score_bot,
                    round=new_res.round,
                    status=new_res.status,
                    winner=new_res.winner
                )
            except Exception:
                return None
            

    async def add_user_to_game(self, user_id: int, chat_id: int)-> GameUser | None:
        if not await self.get_user_by_id(user_id):
            self.create_user(user_id)
        game:Game = await self.get_game_by_chat_id(chat_id)
        if not await self.get_gameuser_by_user_and_game(game.id, user_id):
            await self.create_gameuser(game.id, user_id)
            return None
        return await self.get_gameuser_by_user_and_game(game.id, user_id)



