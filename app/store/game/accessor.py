import typing

from sqlalchemy import func, insert, select, update

from app.base.base_accessor import BaseAccessor
from app.base.base_sqlalchemy import BaseModel
from app.game.models.enums import GameRole, GameStatus
from app.game.models.play import Chat, Game, GameQuestion, GameUser, Question, User

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
            insert_request = insert(User).values(id=user.id, username=user.username).returning(User)
            async with self.app.store.database.session() as session:
                res = await session.execute(insert_request)
                await session.commit()
                return res.scalar_one_or_none()

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
            return existing_game 

        insert_request = insert(Game).values(chat_id=chat_id)
        async with self.app.store.database.session() as session:
            await session.execute(insert_request)
            await session.commit()

        return None
    
    async def create_and_get_game(self, chat_id: int) -> Game:
        existing_game = await self.get_game_by_chat_id(chat_id)
        if existing_game:
            return existing_game  

        insert_request = insert(Game).values(chat_id=chat_id).returning(Game)
        async with self.app.store.database.session() as session:
            res = await session.execute(insert_request)
            await session.commit()
            return res.scalar_one_or_none()

    async def create_gameuser(self, game_id: int, 
                              user_id: int, 
                              game_role:GameRole=GameRole.player
                              ) -> GameUser:
        insert_request = insert(GameUser).values(game_id=game_id, 
                                                 user_id=user_id, 
                                                 game_role=game_role).returning(GameUser)
        async with self.app.store.database.session() as session:
            res = await session.execute(insert_request)
            await session.commit()
            return res.scalar_one_or_none()

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
        select_request = select(User).where(User.id == id).limit(1)
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
                print('11111',new_res)
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
        select_request = (select(Game).where(
            (Game.chat_id == chat_id) & (Game.status == GameStatus.in_progress))
            .limit(1))
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
            
    async def get_last_game_by_chat_id(self, chat_id: int) -> Game | None:
        select_request = (
            select(Game)
            .where(Game.chat_id == chat_id)
            .order_by(Game.id.desc())  # Предполагаем, что ID увеличивается с каждой новой игрой
            .limit(1)
        )
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            new_res = res.scalar_one_or_none()
            if not new_res:
                return None

            return Game(
                id=new_res.id,
                chat_id=new_res.chat_id,
                score_gamers=new_res.score_gamers,
                score_bot=new_res.score_bot,
                round=new_res.round,
                status=new_res.status,
                winner=new_res.winner,
            )

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

    async def get_random_question(self, chat_id: int) -> Question | None:
        game = await self.get_game_by_chat_id(chat_id)
        used_questions_subquery = (
            select(GameQuestion.question_id)
            .join(Game, Game.id == GameQuestion.game_id)
            .where(Game.id == game.id)
        )

        select_request = (
            select(Question)
            .where(Question.id.not_in(used_questions_subquery))
            .order_by(func.random())
            .limit(1)
        )

        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            question = res.scalars().one_or_none()
            return question

    async def get_current_question(self, chat_id: int) -> Question | None:
        game = await self.get_game_by_chat_id(chat_id)
        select_request = (
            select(Question)
            .join(Game, Game.current_question_id == Question.id)
            .where(Game.id == game.id)
        )
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            question = res.scalars().one_or_none()
            return question
        
    async def create_gamequestion(self, game_id: int, question_id: int, user_id: int) -> GameQuestion:
        gameuser = await self.get_gameuser_by_user_and_game(game_id, user_id)
        insert_request = (insert(GameQuestion)
                          .values(game_id=game_id, question_id=question_id, answering_player=gameuser.id)
                          .returning(GameQuestion))
        async with self.app.store.database.session() as session:
            result = await session.execute(insert_request)
            await session.commit()
            return result.scalar_one()
        
    async def create_gamequestion_by_chat_id(self, chat_id: int, question_id: int, user_id:int) -> GameQuestion:
        game = await self.get_game_by_chat_id(chat_id)
        print(game)
        return await self.create_gamequestion(game.id, question_id, user_id)

    async def update_gamequestion(self, gamequestion_id: int, new_question_id: int) -> GameQuestion | None:
        update_request = (
            update(GameQuestion)
            .where(GameQuestion.id == gamequestion_id)
            .values(question_id=new_question_id)
            .returning(GameQuestion)
        )
        async with self.app.store.database.session() as session:
            result = await session.execute(update_request)
            await session.commit()
            return result.scalar_one_or_none()
    
    async def update_gamequestion_answering_player(
        self, game_id: int, user_id: int, new_answering_player: int
    ) -> GameQuestion | None:
        update_request = (
            update(GameQuestion)
            .join(GameUser, GameUser.game_id == GameQuestion.game_id)
            .where(
                (GameUser.game_id == game_id) &
                (GameUser.user_id == user_id) &
                (GameQuestion.game_id == game_id))
            .values(answering_player=new_answering_player)
            .returning(GameQuestion).limit(1)
        )
        async with self.app.store.database.session() as session:
            result = await session.execute(update_request)
            await session.commit()
            return result.scalar_one_or_none()

    async def update_game(self, game_id: int, **fields) -> Game | None:
        if not fields:
            return None

        update_request = (
            update(Game)
            .where(Game.id == game_id)
            .values(**fields)
            .returning(Game)
        )
        async with self.app.store.database.session() as session:
            result = await session.execute(update_request)
            await session.commit()
            return result.scalar_one_or_none()
        
    async def update_game_by_chat_id(self, chat_id: int, **fields) -> Game | None:
        game = await self.get_game_by_chat_id(chat_id)
        return await self.update_game(game.id, **fields)
    
    async def update_object(self, obj):
        async with self.app.store.database.session() as session:
            await session.merge(obj) 
            await session.commit()
        return obj


    async def get_capitan_by_game_id(self, game_id : int) -> User | None:
        req = (select(User)
               .join(GameUser, GameUser.user_id == User.id)
               .join(Game, Game.id == GameUser.game_id)
               .where((Game.id == game_id) &(GameUser.game_role==GameRole.capitan))
               .limit(1)
            )
        async with self.app.store.database.session() as session:
            capitan = await session.execute(req)
            return capitan.scalar_one_or_none()
        
    async def get_all_users_in_game(self, game_id: int) -> list[GameUser]:
        stmt = select(GameUser).where(GameUser.game_id == game_id).order_by(GameUser.id)
        async with self.app.store.database.session() as session:
            result = await session.execute(stmt)
            return result.scalars().all()
        