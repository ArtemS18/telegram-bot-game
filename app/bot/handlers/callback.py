import asyncio
import typing

from app.bot.keyboard import inline_button as kb
from app.bot.states.models import State
from app.game.models.play import User
from app.store.tg_api.models import CallbackQuery, EditMessageText, InlineKeyboardButton, InlineKeyboardMarkup, SendMessage

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

    async def add_user(self, callback: CallbackQuery) -> None:
        chat_id = callback.message.chat.id
        count = await self.db.get_count_users_in_game(chat_id)

        added = await self.db.add_user_to_game(
            User(
                id=callback.from_user.id,
                username=callback.from_user.username,
            ),
            chat_id,
        )

        if not added:
            count+=1
            new_text = f"{callback.message.text}\n{count}) @{callback.from_user.username}"
            edit = EditMessageText(
                chat_id=chat_id,
                message_id=callback.message.message_id,
                text=new_text,
                reply_markup=kb.keyboard_add,
            )
            await self.telegram.edit_message(edit)
            if count >= 3:
                new_text = f"{new_text}\n Можно выбрать капитана и начать игру!"
                edit = EditMessageText(
                    chat_id=chat_id,
                    message_id=callback.message.message_id,
                    text=new_text,
                    reply_markup=kb.keyboard_select,
                )
                self.fsm.set_state(chat_id, self.states.select_capitan)
                await self.telegram.edit_message(edit)
                return
        else:
            await self.telegram.send_message(
                SendMessage(
                    chat_id=chat_id,
                    text=f"🚫 @{callback.from_user.username} уже вступил в команду!",
                )
            )

    async def select_capitan(self, callback: CallbackQuery) -> None:
        chat_id = callback.message.chat.id
        count = await self.db.get_count_users_in_game(chat_id)

        if count == 0:
            await self.telegram.send_message(
                SendMessage(
                    chat_id=chat_id,
                    text="❌ Нет доступных пользователей. Попробуйте позже.",
                )
            )
            return

        capitan_user = await self.db.get_random_capitan(chat_id)

        if not capitan_user:
            await self.telegram.send_message(
                SendMessage(
                    chat_id=chat_id,
                    text="⚠️ Не удалось выбрать капитана. Попробуйте снова.",
                )
            )
            return

        await self.db.set_capitan(chat_id, capitan_user)
        self.fsm.set_state(chat_id, self.states.start_game)

        await self.telegram.send_message(
            SendMessage(
                chat_id=chat_id,
                text=(f"🏆 Бот выбрал @{capitan_user.username} капитаном команды!"
                      "Теперь капитан команды может начать игру."),
                reply_markup=kb.keyboard_start,
            )
        )

    async def start_game(self, callback: CallbackQuery) -> asyncio.Task:
        chat_id = callback.message.chat.id

        await self.telegram.send_message(
            SendMessage(
                chat_id=chat_id,
                text="🚀 Игра началась!",
            )
        )
        await asyncio.sleep(2)

        self.fsm.set_state(chat_id, self.states.question_active)

        task = asyncio.create_task(
            self.app.bot.handlers.game.start_game_round(chat_id)
        )
        return task

    async def quite_game(self, callback: CallbackQuery) -> None:
        chat_id = callback.message.chat.id

        await self.telegram.send_message(
            SendMessage(
                chat_id=chat_id,
                text="👋 Вы вышли из игры. До новых встреч!",
            )
        )
        self.fsm.set_state(chat_id, State())

    async def start_game_with_same_team(self, callback: CallbackQuery) -> None:
        chat_id = callback.message.chat.id
        last_game = await self.db.get_last_game_by_chat_id(chat_id)

        if not last_game:
            await self.telegram.send_message(
                SendMessage(
                    chat_id=chat_id,
                    text="🔍 Предыдущая игра не найдена. Создайте новую игру.",
                )
            )
            self.fsm.set_state(chat_id, State())
            return

        old_users = await self.db.get_all_users_in_game(last_game.id)
        new_game = await self.db.create_and_get_game(chat_id=chat_id)

        for user in old_users:
            await self.db.create_gameuser(
                game_id=new_game.id,
                user_id=user.user_id,
                game_role=user.game_role,
            )

        self.fsm.set_state(chat_id, self.states.start_game)

        await self.telegram.send_message(
            SendMessage(
                chat_id=chat_id,
                text="🚀 Новая игра началась с тем же составом!",
                reply_markup=kb.keyboard_start,
            )
        )
    async def answering_player(self, callback: CallbackQuery) -> None:
        game = await self.db.get_game_by_chat_id(callback.message.chat.id)
        user_id = int(callback.data.split('_')[1].strip())
        aswering = await self.db.get_gameuser_by_user_and_game(game.id, user_id)
        await self.db.update_gamequestion_answering_player(game.id, user_id, aswering.id)
        await self.telegram.send_message(
            SendMessage(
                chat_id=callback.message.chat.id,
                text="Теперь этот игорок отвечает своим следующим сообщением!",
            )
        )

    async def get_answer(self, callback: CallbackQuery) -> None:
        chat_id = callback.message.chat.id
        print(1111)
        game = await self.db.get_game_by_chat_id(chat_id)
        gameusers = await self.db.get_all_users_in_game(game.id)
        buttons = []
        for idx, gameuser in enumerate(gameusers):
            user = await self.db.get_user_by_id(gameuser.user_id)
            button = InlineKeyboardButton(
                text=f"{idx+1}. @{user.username}",
                callback_data=f"user_{user.id}"
            )
            buttons.append([button])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        m = await self.telegram.send_message(
            SendMessage(
                chat_id=chat_id,
                text="Капитан может выбрать пользователя.",
                reply_markup=keyboard
            )
        )
        print(m)

