import asyncio
import typing

from app.bot.keyboard import inline_button as kb
from app.game.models.enums import GameStatus
from app.game.models.play import User
from app.store.tg_api.models import CallbackQuery, EditMessageText, InlineKeyboardButton, InlineKeyboardMarkup, SendMessage

if typing.TYPE_CHECKING:
    from app.bot.states.models import BotState
    from app.store.game.accessor import GameAccessor
    from app.web.app import Application


class CallbackHandler:
    def __init__(self, app: "Application"):
        self.app: "Application" = app
        self.fsm = app.bot.fsm
        self.telegram = app.store.tg_api
        self.db: "GameAccessor" = app.store.game
        self.states: "BotState" = app.bot.states
        self.queues = app.bot.answer_queues
        self.active_tasks =  self.app.bot.active_tasks
        self.ready_queues =  app.bot.ready_queues
        self.asyncio = app.bot.utils.asyncio

    async def add_user(self, callback: CallbackQuery) -> None:
        chat_id = callback.message.chat.id
        game = await self.db.get_game_by_chat_id(chat_id)
        if not game:
            return
        users_in_game = await self.db.get_all_users_in_game(game.id)
        count = len(users_in_game)
        added = await self.db.add_user_to_game(
            User(
                id=callback.from_user.id,
                username=callback.from_user.username,
            ),
            chat_id,
        )

        if not added: 
            game = await self.db.get_game_by_chat_id(chat_id)
            users_in_game = await self.db.get_all_users_in_game(game.id)
            count = len(users_in_game)
            new_text = f"✨ Игра создана! Необходимо набрать (3/{count}) участника для начала игры\n"
            for i, user in enumerate(users_in_game, start=1): 
                useri = await self.db.get_user_by_id(user.user_id)
                new_text += f"{i}) @{useri.username}\n"

            if count >= 2:
                
                new_text += "\nМожно выбрать капитана и начать игру!"
                await self.fsm.set_state(chat_id, self.states.select_capitan)

            edit_markup = kb.keyboard_add if count < 2 else kb.keyboard_select 
            edit = EditMessageText(
                chat_id=chat_id,
                message_id=callback.message.message_id,
                text=new_text,
                reply_markup=edit_markup,
            )
            await self.telegram.edit_message(edit)

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
        await self.fsm.set_state(chat_id, self.states.start_game)
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
        await self.ready_queues[chat_id].put("GO")
        await self.telegram.send_message(
            SendMessage(
                chat_id=chat_id,
                text="🚀 Игра началась!",
            )
        )
        
        await self.fsm.set_state(chat_id, self.states.question_active)
        task = asyncio.create_task(
            self.app.bot.handlers.game.start_round(callback.message)
        )
        if not self.app.bot.active_tasks.get(chat_id):
            self.app.bot.active_tasks[chat_id] = []

        self.active_tasks[chat_id].append(task)
        task.add_done_callback(lambda t: self.active_tasks.pop(chat_id, None))

    async def quite_game(self, callback: CallbackQuery) -> None:
        chat_id = callback.message.chat.id
        game = await self.db.get_last_game_by_chat_id(chat_id)
        count = len(await self.db.delete_gameuser_by_game_user(game.id, callback.from_user.id))
        if count == 0:
            await self.ready_queues[chat_id].put("GO")
            edit = EditMessageText(
                chat_id=chat_id,
                message_id=callback.message.message_id,
                text=f"Все участники покинули команду /start для создания нового",
            )
            await self.telegram.edit_message(edit)
            await self.db.update_game(game.id, status=GameStatus.end)
            await self.fsm.set_state(chat_id, self.states.none)
            return
        
        game = await self.db.get_game_by_chat_id(chat_id)
        users_in_game = await self.db.get_all_users_in_game(game.id)
        count = len(users_in_game)
        new_text = f"✨ Игра создана! Необходимо набрать (3/{count}) участника для начала игры\n"
        for i, user in enumerate(users_in_game, start=1): 
            useri = await self.db.get_user_by_id(user.user_id)
            new_text += f"{i}) @{useri.username}\n"

        if count >= 2:
            new_text += "\nМожно выбрать капитана и начать игру!"
            await self.fsm.set_state(chat_id, self.states.select_capitan)

        edit_markup = kb.keyboard_add if count < 2 else kb.keyboard_select 
        edit = EditMessageText(
            chat_id=chat_id,
            message_id=callback.message.message_id,
            text=new_text,
            reply_markup=edit_markup,
        )
        await self.telegram.edit_message(edit)

    async def userquite_game(self, callback: CallbackQuery) -> None:
        chat_id = callback.message.chat.id
        game = await self.db.get_last_game_by_chat_id(chat_id)
        count = len(await self.db.delete_gameuser_by_game_user(game.id, callback.from_user.id))
        if count == 0:
            await self.ready_queues[chat_id].put("GO")
            edit = EditMessageText(
                chat_id=chat_id,
                message_id=callback.message.message_id,
                text=f"Все участники покинули команду /start для создания нового",
            )
            await self.telegram.edit_message(edit)
            await self.db.update_game(game.id, status=GameStatus.end)
            await self.fsm.set_state(chat_id, self.states.none)
            return
        await self.telegram.send_message(
            SendMessage(
                chat_id=chat_id,
                text=f"@{callback.from_user.username} покинул игру.",
            )
        )

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
            await self.fsm.set_state(chat_id, self.states.none)
            return

        old_users = await self.db.get_all_users_in_game(last_game.id)
        new_game = await self.db.create_and_get_game(chat_id=chat_id)

        for user in old_users:
            await self.db.create_gameuser(
                game_id=new_game.id,
                user_id=user.user_id,
                game_role=user.game_role,
            )
        

        await self.fsm.set_state(chat_id, self.states.add_users)
        users_in_game = await self.db.get_all_users_in_game(new_game.id)
        count = len(users_in_game)
        new_text = f"✨ Игра продолжена! Необходимо набрать (3/{count}) участника для начала игры\n"
        for i, user in enumerate(users_in_game, start=1): 
            useri = await self.db.get_user_by_id(user.user_id)
            new_text += f"{i}) @{useri.username}\n"

        if count >= 2:
            new_text += "\nМожно выбрать капитана и начать игру!"
            await self.fsm.set_state(chat_id, self.states.select_capitan)

        edit_markup = kb.keyboard_add if count < 2 else kb.keyboard_select 
        send = SendMessage(
            chat_id=chat_id,
            text=new_text,
            reply_markup=edit_markup,
        )
        ms = await self.telegram.send_message(send)
       
        

    async def answering_player(self, callback: CallbackQuery) -> None:
        game = await self.db.get_game_by_chat_id(callback.message.chat.id)
        if not game:
            return 
        user_id = int(callback.data.split('_')[1].strip())

        aswering = await self.db.get_gameuser_by_user_and_game(game.id, user_id)
        await self.db.update_gamequestion_answering_player(game.id, user_id, aswering.id)

        await self.fsm.set_state(callback.message.chat.id, self.states.check_answer)
        user = await self.db.get_user_by_id(user_id)
        await self.telegram.edit_message(
            EditMessageText(
                message_id=callback.message.message_id,
                chat_id=callback.message.chat.id,
                text=f"Теперь @{user.username} отвечает своим следующим сообщением!",
            )
        )

    async def get_answer(self, callback: CallbackQuery) -> None:
        chat_id = callback.message.chat.id
        game = await self.db.get_game_by_chat_id(chat_id)
        if not game:
            return 
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

        await self.fsm.set_state(chat_id, self.states.select_user)
        m = await self.telegram.send_message(
            SendMessage(
                chat_id=chat_id,
                text="Капитан может выбрать пользователя.",
                reply_markup=keyboard
            )
        )

