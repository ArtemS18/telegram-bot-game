import typing

from app.game.models.enums import GameRole
from app.store.tg_api.models import SendMessage

if typing.TYPE_CHECKING:
    from app.store.game.accessor import GameAccessor
    from app.web.app import Application


class AuthMiddleware:
    def __init__(self, app: "Application"):
        self.app: "Application" = app
        self.telegram = app.store.tg_api
        self.db: "GameAccessor" = app.store.game

    async def captain_only_middleware(self, handler, *args, **kwargs):
        """
        Middleware to ensure only the captain can execute the command.
        :param handler: Handler to execute if the user is authorized.
        """
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
        game = await self.db.get_game_by_chat_id(chat_id)
        if not game:
            await self.telegram.send_message(
                SendMessage(
                    chat_id=chat_id,
                    text="Игра не найдена. Создайте игру перед началом.",
                )
            )
            return

        gameuser = await self.db.get_gameuser_by_user_and_game(game.id, user_id)
        if not gameuser or gameuser.game_role != GameRole.capitan:
            await self.telegram.send_message(
                SendMessage(
                    chat_id=chat_id,
                    text="Только капитан команды может использовать эту команду.",
                )
            )
            return

        await handler(*args, **kwargs)
