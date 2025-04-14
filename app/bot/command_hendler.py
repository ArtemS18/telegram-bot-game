import typing

from app.store.tg_api.models import (
    CallbackQuery,
    EditMessageText,
    Message,
    SendMessage,
)

from .keyboard import inline_button as kb

from .models.state_manager import FSM, State

if typing.TYPE_CHECKING:
    from app.web.app import Application

class CommandHandler:
    def __init__(self, app: "Application"):
        self.app = app
        self.fsm = FSM()

    async def start_command(self, message: Message):
        text = "Привет давай поиграем в Игру...."
        answer = SendMessage(
            chat_id=message.chat.id, 
            text=text, 
            reply_markup=kb.keyboard_start
        )
        await self.app.store.tg_api.send_message(answer)
        self.fsm.set_state(message.chat.id, State("START"))

    async def add_user(self, message: Message):
        text="Начнем набор игроков"
        answer = SendMessage(
            chat_id=message.chat.id, 
            text=text
        )
        await self.app.store.tg_api.send_message(answer)
        self.fsm.set_state(message.chat.id, State())

    async def query(self, callback: CallbackQuery):
        last = callback.message.text
        text = f"{last} \n @{callback.from_user.username}"
        edit = EditMessageText(
            chat_id=callback.message.chat.id, 
            message_id=callback.message.message_id,
            text=text,
            reply_markup=kb.keyboard_start
        )
        await self.app.store.tg_api.edit_message(edit)
        # self.fsm.set_state(callback.message.chat.id, State())

    

    