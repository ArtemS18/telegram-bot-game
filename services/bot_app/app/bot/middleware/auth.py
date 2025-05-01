import asyncio
from dataclasses import dataclass
import typing

from app.bot.states.state_manager import FSM
from app.game.models.enums import BotState, GameRole
from app.store.tg_api.models import CallbackQuery, Message, SendMessage
from app.game.models.play import GameUser

if typing.TYPE_CHECKING:
    from app.store.game.accessor import GameAccessor
    from app.web.app import Application

@dataclass
class AuthData:
    gameuser: GameUser | None = None
    chat_id : int | None = None
    obj: Message | CallbackQuery  | None = None
    

class AuthMiddleware:
    def __init__(self, app: "Application"):
        self.app: "Application" = app
        self.telegram = app.store.tg_api
        self.db: "GameAccessor" = app.store.game
        self.active_tasks =  self.app.bot.active_tasks
        self.handler = self.app.bot.handlers
        self.fsm: "FSM" = app.bot.fsm
        self.states: "BotState" = app.bot.states


    async def auth_user(self, *args, **kwargs) -> AuthData:
        obj = kwargs.get("callback") or kwargs.get("message")
        if not obj:
            return
        user_id = getattr(obj.from_user, "id", None)
        chat_id = (
            getattr(getattr(obj, "message", obj), "chat", None).id
            if hasattr(obj, "message")
            else obj.chat.id
        )
        if not user_id or not chat_id:
            return
        game = await self.db.get_last_game_by_chat_id(chat_id)
        if not game:
            await self.telegram.send_message(
                SendMessage(
                    chat_id=chat_id,
                    text="Игра не найдена. Создайте игру перед началом.",
                )
            )
            return

        gameuser = await self.db.get_gameuser_by_user_and_game(game.id, user_id)
        return AuthData(gameuser=gameuser, chat_id=chat_id, obj=obj)
    

    async def captain_only_middleware(self, handler, *args, **kwargs):
        data = await self.auth_user(*args, **kwargs)
        if not data or not data.gameuser:
            return 
        if not data.gameuser or data.gameuser.game_role != GameRole.capitan:
            return
        await handler(*args, **kwargs)


    async def player_only_middleware(self, handler, *args, **kwargs):
        data = await self.auth_user(*args, **kwargs)
        print(data.gameuser, data.gameuser.game_role)
        if not data or not data.gameuser:
            return 
            
        if not data.gameuser or data.gameuser.game_role not in [GameRole.capitan, GameRole.player]:
            return
        await handler(*args, **kwargs)

    async def answering_only_middleware(self, handler, *args, **kwargs):
        data = await self.auth_user(*args, **kwargs)
        if not data or not data.gameuser:
            return 
        current_question = await self.db.get_current_gamequestion(data.chat_id)
        if not current_question or data.gameuser.id != current_question.answering_player:
            return
        if not self.app.bot.active_tasks.get(data.chat_id):
            self.app.bot.active_tasks[data.chat_id] = []
        task=asyncio.create_task(handler(*args, **kwargs))
        self.active_tasks[data.chat_id].append(task)
        task.add_done_callback(lambda t: self.active_tasks.pop(data.chat_id, None))
