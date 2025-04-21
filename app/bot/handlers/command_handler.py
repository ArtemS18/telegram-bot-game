import typing

from app.store.tg_api.models import (
    CallbackQuery,
    EditMessageText,
    Message,
    SendMessage,
)

from app.bot.keyboard import inline_button as kb

if typing.TYPE_CHECKING:
    from app.web.app import Application

class CommandHandler:
    def __init__(self, app: "Application"):
        self.app = app
        self.telegram = app.store.tg_api
        self.fsm = app.bot.fsm
        self.states = app.bot.states
        self.db = app.store.game

    async def start_command(self, message: Message):
        text = "Привет давай поиграем в Игру.... для начала создания лобби /create_game"
        answer = SendMessage(
            chat_id=message.chat.id, 
            text=text, 
        )
        await self.telegram.send_message(answer)
        user = await self.db.get_chat_by_id(message.chat.id)
        if not user:
            await self.db.create_chat(message.chat.id)

        self.fsm.set_state(message.chat.id,  self.states.creation_game)

    async def creation_game(self, message: Message):
        await self.db.create_game(message.chat.id)
        text=f"Игра создана @{message.from_user.username} \n Список участников: \n @{message.from_user.username}"
        answer = SendMessage(
            chat_id=message.chat.id, 
            text=text,
            reply_markup=kb.keyboard_start
        )
        await self.telegram.send_message(answer)
        self.fsm.set_state(message.chat.id,  self.states.add_users)
        # self.fsm.set_state(callback.message.chat.id, State())

    

    