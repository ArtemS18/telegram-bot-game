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
        if not gameuser or gameuser.game_role != GameRole.capitan:
            await self.telegram.send_message(
                SendMessage(
                    chat_id=chat_id,
                    text="Только капитан команды может использовать эту команду.",
                )
            )
            return

        await handler(*args, **kwargs)


    async def player_only_middleware(self, handler, *args, **kwargs):
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
        if not gameuser:
            await self.telegram.send_message(
                SendMessage(
                    chat_id=chat_id,
                    text="Вы не участвуете в этой игре.",
                )
            )
            return

        if gameuser.game_role not in [GameRole.capitan, GameRole.player]:
            await self.telegram.send_message(
                SendMessage(
                    chat_id=chat_id,
                    text="У вас нет доступа к этой команде.",
                )
            )
            return

        await handler(*args, **kwargs)

    async def answering_only_middleware(self, handler, *args, **kwargs):
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
        current_question = await self.db.get_current_gamequestion(chat_id)
        if gameuser.id != current_question.answering_player:
            await self.telegram.send_message(
                SendMessage(
                    chat_id=chat_id,
                    text="Вы не можете отвечать.",
                )
            )
            return
        await handler(*args, **kwargs)
