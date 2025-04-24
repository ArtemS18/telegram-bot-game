from dataclasses import dataclass
import typing

from app.game.models.enums import GameRole
from app.store.tg_api.models import SendMessage
from app.game.models.play import GameUser

if typing.TYPE_CHECKING:
    from app.store.game.accessor import GameAccessor
    from app.web.app import Application

@dataclass
class AuthData:
    gameuser: GameUser | None = None
    chat_id : int | None = None
    

class AuthMiddleware:
    def __init__(self, app: "Application"):
        self.app: "Application" = app
        self.telegram = app.store.tg_api
        self.db: "GameAccessor" = app.store.game


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
        return AuthData(gameuser=gameuser, chat_id=chat_id)

    async def captain_only_middleware(self, handler, *args, **kwargs):
        data = await self.auth_user(*args, **kwargs)
        if not data:
            return 
        if not data.gameuser or data.gameuser.game_role != GameRole.capitan:
            await self.telegram.send_message(
                SendMessage(
                    chat_id=data.chat_id,
                    text="Только капитан команды может использовать эту команду.",
                )
            )
            return
        await handler(*args, **kwargs)


    async def player_only_middleware(self, handler, *args, **kwargs):
        data = await self.auth_user(*args, **kwargs)
        if not data:
            return 
        if not data.gameuser or data.gameuser.game_role not in [GameRole.capitan, GameRole.player]:
            await self.telegram.send_message(
                SendMessage(
                    chat_id=data.chat_id,
                    text="У вас нет доступа к этой команде.",
                )
            )
            return
        await handler(*args, **kwargs)

    async def answering_only_middleware(self, handler, *args, **kwargs):
        data = await self.auth_user(*args, **kwargs)
        if not data:
            return 
        current_question = await self.db.get_current_gamequestion(data.chat_id)
        if data.gameuser.id != current_question.answering_player:
            await self.telegram.send_message(
                SendMessage(
                    chat_id=data.chat_id,
                    text="Вы не можете отвечать.",
                )
            )
            return
        await handler(*args, **kwargs)
