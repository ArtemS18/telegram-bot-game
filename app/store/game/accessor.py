import typing

from sqlalchemy import func, insert, select, update

from app.base.base_accessor import BaseAccessor
from app.base.base_sqlalchemy import BaseModel
from app.game.models.enums import GameRole, GameStatus, QuestionStatus
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

    async def create_chat(self, chat_id: int) -> Chat:
        if not await self.get_chat_by_id(chat_id):
            insert_request = insert(Chat).values(chat_id=id)
            async with self.app.store.database.session() as session:
                await session.execute(insert_request)
                await session.commit()
        return await self.get_chat_by_id(id)

    async def create_game(self, chat_id: int) -> Game:
        existing_game = await self.get_game_by_chat_id(chat_id)
        
        if existing_game is not None:
            return existing_game 
        if existing_game is not None and existing_game.round == 0:
                await self.update_game(existing_game.id, status=GameStatus.end)

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

    async def create_gameuser(
            self, game_id: int, 
            user_id: int, 
            game_role:GameRole=GameRole.player
        ) -> GameUser:
        insert_request = (
            insert(GameUser)
            .values(
            game_id=game_id, 
            user_id=user_id, 
            game_role=game_role
            ).returning(GameUser)
        )
        async with self.app.store.database.session() as session:
            res = await session.execute(insert_request)
            await session.commit()
            return res.scalar_one_or_none()

    async def get_chat_by_id(self, id: int) -> User | None:
        select_request = select(Chat).where(Chat.id == id)
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            new_res = res.scalar_or_none()
            return new_res

    async def get_user_by_id(self, id: int) -> User | None:
        select_request = select(User).where(User.id == id).limit(1)
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            new_res = res.scalar_or_none()
            return new_res

    async def get_gameuser_by_id(self, id: int) -> GameUser | None:
        select_request = select(GameUser).where(GameUser.id == id)
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            new_res = res.scalar_or_none()
            return new_res

    async def get_gameuser_by_user_and_game(self, game_id: int, user_id: int) -> GameUser | None:
        select_request = (
            select(GameUser)
            .where(
            (GameUser.game_id == game_id) & (GameUser.user_id == user_id))
            .limit(1)
        )
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            new_res = res.scalar_one_or_none()
            return new_res

    async def get_game_by_id(self, id: int) -> Game | None:
        select_request = select(Game).where(Game.id == id).limit(1)
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            new_res = res.scalar_one_or_none()
            return new_res

    async def get_game_by_chat_id(self, chat_id: int) -> Game | None:
        select_request = (select(Game).where(
            (Game.chat_id == chat_id) & (Game.status == GameStatus.in_progress))
            .limit(1))
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            new_res = res.scalar_one_or_none()
            return new_res
            
    async def get_last_game_by_chat_id(self, chat_id: int) -> Game | None:
        select_request = (
            select(Game)
            .where(Game.chat_id == chat_id)
            .order_by(Game.id.desc()) 
            .limit(1)
        )
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            new_res = res.scalar_one_or_none()
            return new_res

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
            .where(GameUser.game_id == game.id)
            .order_by(func.random())
            .limit(1)
        )
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            user = res.scalar_one_or_none()
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
        update_request = (
                update(GameUser)
                .where((GameUser.game_id == game.id) & (GameUser.user_id == capitan.id))
                .values(game_role=GameRole.capitan)
            )
        async with self.app.store.database.session() as session:
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
            question = res.scalar_one_or_none()
            return question

    async def get_current_question(self, chat_id: int) -> Question | None:
        game = await self.get_game_by_chat_id(chat_id)
        if not game:
            return None
        
        select_request = (
            select(Question)
            .join(GameQuestion, GameQuestion.question_id == Question.id)
            .join(Game, Game.id==GameQuestion.game_id)
            .where((Game.id == game.id) & (GameQuestion.status == QuestionStatus.in_progress))
            .order_by(GameQuestion.id)
            .limit(1)
        )
        async with self.app.store.database.session() as session:
            res = await session.execute(select_request)
            question = res.scalars().one_or_none()
            return question
        
    async def get_current_gamequestion(self, chat_id: int) -> GameQuestion | None:
        game = await self.get_game_by_chat_id(chat_id)
        if not game:
            return None
        select_request = (
            select(GameQuestion)
            .join(Game, Game.id==GameQuestion.game_id)
            .where((Game.id == game.id) & (GameQuestion.status == QuestionStatus.in_progress) )
            .order_by(GameQuestion.id)
            .limit(1)
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
        
    async def create_gamequestion_by_chat_id(self, chat_id: int, question_id: int, user_id:int) -> GameQuestion|None:
        game = await self.get_game_by_chat_id(chat_id)
        if not game:
            return None
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
        async with self.app.store.database.session() as session:
            select_stmt = (
                select(GameQuestion)
                .join(GameUser, GameUser.game_id == GameQuestion.game_id)
                .where(
                    (GameUser.game_id == game_id) &
                    (GameUser.user_id == user_id) &
                    (GameQuestion.status == QuestionStatus.in_progress)
                )
                .limit(1)
            )

            result = await session.execute(select_stmt)
            game_question = result.scalar_one_or_none()

            if game_question:
                print(game_question.answering_player, new_answering_player)
                game_question.answering_player = new_answering_player 
                await session.merge(game_question) 
                await session.commit()  # Обновляем объект из БД после коммита
                return game_question
            else:
                return None  # Если GameQuestion не найден




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
        