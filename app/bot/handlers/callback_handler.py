import asyncio
import typing

from app.bot.keyboard import inline_button as kb
from app.game.models.play import User
from app.store.tg_api.models import CallbackQuery, EditMessageText, SendMessage

if typing.TYPE_CHECKING:
    from app.bot.states.models import BotStates
    from app.store.game.accessor import GameAccessor
    from app.web.app import Application


class CallbackHandler:
    def __init__(self, app: "Application"):
        self.app: "Application" = app
        self.fsm = app.bot.fsm
        self.telegram = app.store.tg_api
        self.db: "GameAccessor" = app.store.game
        self.states: "BotStates" = app.bot.states

    async def add_user(self, callback: CallbackQuery):
        count = await self.db.get_count_users_in_game(callback.message.chat.id)
        if count > 4:
            last_text = callback.message.text
            new_text = f"{last_text}\n Можно выбрать капитана и начать игру! "
            edit = EditMessageText(
                chat_id=callback.message.chat.id,
                text=new_text,
                message_id=callback.message.message_id,
                reply_markup=kb.keyboard_select,
            )
            self.fsm.set_state(
                callback.message.chat.id, 
                self.states.select_capitan
            )
            await self.telegram.edit_message(edit)
            return None

        if not await self.db.add_user_to_game(
            User(
                id=callback.from_user.id, 
                username=callback.from_user.username),
            callback.message.chat.id,
        ):
            count = await self.db.get_count_users_in_game(
                callback.message.chat.id
            )
            last_text = callback.message.text
            new_text = f"{last_text} \n {count}) @{callback.from_user.username}"
            edit = EditMessageText(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text=new_text,
                reply_markup=kb.keyboard_add,
            )
            await self.telegram.edit_message(edit)
        else:
            answer = SendMessage(
                chat_id=callback.message.chat.id,
                text=f"@{callback.from_user.username} уже вступил в команду!",
            )
            await self.telegram.send_message(answer)

    async def select_capitan(self, callback: CallbackQuery):
        count = await self.db.get_count_users_in_game(
            callback.message.chat.id
        )
        if count == 0:
            answer = SendMessage(
                chat_id=callback.message.chat.id,
                text="Нет доступных пользователей",
            )
            await self.telegram.send_message(answer)
            return

        capitan_user = await (self.db
                              .get_random_capitan(callback.message.chat.id))
        if not capitan_user:
            answer = SendMessage(
                chat_id=callback.message.chat.id,
                text="Не удалось выбрать капитана. Попробуйте снова.",
            )
            await self.telegram.send_message(answer)
            return

        await self.db.set_capitan(callback.message.chat.id, capitan_user)

        answer = SendMessage(
            chat_id=callback.message.chat.id,
            text=f"Бот выбрал @{capitan_user.username} капитаном команды",
            reply_markup=kb.keyboard_start,
        )
        self.fsm.set_state(
            callback.message.chat.id, 
            self.states.start_game
        )
        await self.telegram.send_message(answer)

    async def start_game(self, callback: CallbackQuery):
        answer = SendMessage(
            chat_id=callback.message.chat.id,
            text="Игра началась",
        )
        await self.telegram.send_message(answer)

        await asyncio.sleep(2)
        self.fsm.set_state(
            callback.message.chat.id,
            self.states.question_active
        )

        task = asyncio.create_task(
            self.app.bot.handlers.game.start_game_round(callback.message)
        )
        return task
