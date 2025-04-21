import typing

from sqlalchemy import func, insert, select, update

from app.base.base_accessor import BaseAccessor
from app.base.base_sqlalchemy import BaseModel
from app.game.models.enums import GameRole
from app.game.models.play import Chat, Game, GameUser, Question, User

if typing.TYPE_CHECKING:
    from aiohttp.web import Application


class GameAccessor(BaseAccessor):

    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    async def create_tables(self):
        async with self.app.store.database.engine.begin() as conn:

            await conn.run_sync(BaseModel.metadata.create_all)
            self.app.log.info("Create TABLES")

    async def create_user(self, user: User) -> User:
        if not await self.get_user_by_id(user.id):
            insert_request = insert(User).values(id=user.id, username=user.username)
            async with self.app.store.database.session() as session:
                await session.execute(insert_request)
                await session.commit()
        return await self.get_user_by_id(user.id)

    async def create_chat(self, id: int) -> Chat:
        if not await self.get_chat_by_id(id):
            insert_request = insert(Chat).values(id=id)
            async with self.app.store.database.session() as session:
                await session.execute(insert_request)
                await session.commit()
        return await self.get_chat_by_id(id)

    async def create_game(self, chat_id: int) -> Game:
        existing_game = await self.get_game_by_chat_id(chat_id)
        if existing_game:
            return existing_game  # Return the existing game if found

        insert_request = insert(Game).values(chat_id=chat_id)
        async with self.app.store.database.session() as session:
            await session.execute(insert_request)
            await session.commit()

        return await self.get_game_by_chat_id(chat_id)

    async def create_gameuser(self, game_id: int, user_id: int) -> GameUser:
        insert_request = insert(GameUser).values(game_id=game_id, user_id=user_id)
        async with self.app.store.database.session() as session:
            await session.execute(insert_request)
            await session.commit()
        return await self.get_game_by_id(game_id)

    async def get_chat_by_id(self, id: int) -> User | None:
        select_request = select(Chat).where(Chat.id == id)
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            try:
                new_res = res.scalars().one()
                return Chat(id=new_res.id, bot_state=new_res.bot_state)
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
                    username=new_res.username,
                    is_admin=new_res.is_admin,
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
                    game_role=new_res.game_role,
                )
            except Exception:
                return None

    async def get_gameuser_by_user_and_game(
        self, game_id: int, user_id: int
    ) -> GameUser | None:
        select_request = (
            select(GameUser)
            .where((GameUser.game_id == game_id) 
                   & (GameUser.user_id == user_id))
            .limit(1)
        )

        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            new_res = res.scalar_one_or_none()

            if new_res is None:
                return None

            return GameUser(
                id=new_res.id,
                user_id=new_res.user_id,
                game_id=new_res.game_id,
                game_role=new_res.game_role,
            )

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
                    winner=new_res.winner,
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
                    winner=new_res.winner,
                )
            except Exception:
                return None

    async def get_count_users_in_game(self, chat_id: int) -> int:
        game = await self.get_game_by_chat_id(chat_id)
        if not game:
            return 0

        select_request = select(func.count()).where(GameUser.game_id == game.id)
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            try:
                count = res.scalar()
                return count
            except Exception:
                return 0

    async def get_random_capitan(self, chat_id: int) -> User | None:
        game = await self.get_game_by_chat_id(chat_id)
        select_request = (
            select(User)
            .join(GameUser, GameUser.user_id == User.id)
            .where(GameUser.game_id == game.id)  # GameUser.game_role == 'player'
            .order_by(func.random())
            .limit(1)
        )

        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            user = res.scalars().one_or_none()
            return user

    async def add_user_to_game(
            self, 
            user: User, 
            chat_id: int) -> GameUser | None:
        if not await self.get_user_by_id(user.id):
            await self.create_user(user)
        game = await self.get_game_by_chat_id(chat_id)
        # gameuser = await self.get_gameuser_by_user_and_game(game.id, user.id)
        # if gameuser:
        #    return gameuser
        await self.create_gameuser(game.id, user.id)
        return None

    async def update_game_by_chat_id(
            self, 
            chat_id: int, 
            **kwargs) -> Game | None:

        select_request = (
            update(GameUser).where(GameUser.id == id).values(game_role=GameRole.capitan)
        )
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            game = res.scalars().one_or_none()

            if not game:
                return None

            for key, value in kwargs.items():
                if hasattr(game, key):
                    setattr(game, key, value)

            await session.commit()
            await session.refresh(game)
            return game

    async def set_capitan(self, chat_id: int, capitan: User) -> bool:
        game = await self.get_game_by_chat_id(chat_id)
        if not game:
            return False

        async with self.app.store.database.session() as session:
            update_request = (
                update(GameUser)
                .where((GameUser.game_id == game.id) 
                       & (GameUser.user_id == capitan.id))
                .values(game_role=GameRole.capitan)
            )
            await session.execute(update_request)
            await session.commit()
            return True

    async def get_random_question(self) -> Question | None:
        select_request = select(Question).order_by(func.random()).limit(1)
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            question = res.scalars().one_or_none()
            return question

    async def get_current_question(self, chat_id: int) -> Question | None:
        select_request = (
            select(Question)
            .join(Game, Game.current_question_id == Question.id)
            .where(Game.chat_id == chat_id)
        )
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            question = res.scalars().one_or_none()
            return question
