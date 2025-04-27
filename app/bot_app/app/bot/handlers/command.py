import asyncio
import typing

from app.bot.keyboard import inline_button as kb
from app.bot.models.dataclasses import Answer
from app.game.models.enums import GameStatus
from app.game.models.play import Game, User
from app.store.tg_api.models import EditMessageText, InlineKeyboardButton, InlineKeyboardMarkup, Message, SendMessage

if typing.TYPE_CHECKING:
    from app.bot.states.models import BotState
    from app.store.game.accessor import GameAccessor
    from app.web.app import Application


class CommandHandler:
    def __init__(self, app: "Application"):
        self.app = app
        self.telegram = app.store.tg_api
        self.fsm = app.bot.fsm
        self.states: "BotState" = app.bot.states
        self.db: "GameAccessor" = app.store.game
        self.answer_queues = app.bot.answer_queues
        self.asyncio = app.bot.utils.asyncio

    async def start_command(self, message: Message) -> None:
        text = (
            "🎉 Привет! Готов поиграть в Что? Где? Когда?? \n"
            "Для начала создай лобби командой /create_game "
        )

        await self.telegram.send_message(
            SendMessage(chat_id=message.chat.id, text=text)
        )

        user = await self.db.get_chat_by_id(message.chat.id)
        if not user:
            await self.db.create_chat(message.chat.id)

        await self.fsm.set_state(message.chat.id, self.states.creation_game)

    async def creation_game(self, message: Message) -> None:
        game: Game = await self.db.create_game(message.chat.id)
        if game and await self.db.get_capitan_by_game_id(game.id):
            capitan = await self.db.get_capitan_by_game_id(game.id)
            answer = SendMessage(
                chat_id=message.chat.id,
                text=(
                    "🎮 У вас уже есть незавершенная игра в этом чате! \n"
                    f"🏆 Раунд: {game.round}  Счёт: {game.score_gamers}:{game.score_bot}\n"
                    f"Капитан {capitan.username}\n"
                    "Нажмите на кнопку, чтобы продолжить! ⏩"
                ),
                reply_markup=kb.keyboard_start,
            )
            await self.fsm.set_state(message.chat.id, self.states.start_game)
            await self.telegram.send_message(answer)
            return
        text = (
            f"✨ Игра создана! Необходимо набрать (3/1) участника для начала игры\n"
            f"Список участников:\n1) @{message.from_user.username}"
        )

        await self.db.add_user_to_game(
            User(id=message.from_user.id, 
                username=message.from_user.username),
            message.chat.id,
        )

        answer = SendMessage(
            chat_id=message.chat.id,
            text=text,
            reply_markup=kb.keyboard_add,
        )
        await self.fsm.set_state(message.chat.id, self.states.add_users)
        ms = await self.telegram.send_message(answer)
        game = await self.db.get_game_by_chat_id(message.chat.id)
        try:
            team = await self.asyncio.start_timer_team(message.chat.id)
            self.app.log.info(team)
        except asyncio.TimeoutError:
            edit = EditMessageText(
                chat_id=message.chat.id,
                text="Лобби удалено из-за превышения лимита ожидания (30 сек)",
                message_id=ms.message_id
            )
            await self.telegram.edit_message(edit)
            await self.db.update_game(game.id, status=GameStatus.end)
            await self.fsm.set_state(message.chat.id, self.states.none)


    async def answer_command(self, message: Message) -> None:
        chat_id = message.chat.id
        text = message.text
        if not text:
            await self.telegram.send_message(
                SendMessage(
                    chat_id=chat_id,
                    text="Отвечайте господин Друзь!"
                )
            )
            return

        answer_text = text.strip()
        await self.answer_queues[chat_id].put(
            Answer(
                text=answer_text,
                chat_id=chat_id,
                user_id=message.from_user.id,
            )
        )
