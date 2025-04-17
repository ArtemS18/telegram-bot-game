import typing

from app.store.tg_api.models import (
    CallbackQuery,
    EditMessageText,
)

from app.bot.keyboard import inline_button as kb


if typing.TYPE_CHECKING:
    from app.web.app import Application

class CallbackHandler:
    def __init__(self, app: "Application"):
        self.app = app
        self.fsm = app.bot.fsm
        self.telegram = app.store.tg_api
        self.db = app.store.game

    async def add_user(self, callback: CallbackQuery):
        last_text = callback.message.text
        if await self.db.get_user_by_id(callback.from_user.id):
            return None
        await self.db.create_user(callback.from_user.id)
        new_text = f"{last_text} \n @{callback.from_user.username}"
        edit = EditMessageText(
            chat_id=callback.message.chat.id, 
            message_id=callback.message.message_id,
            text=new_text,
            reply_markup=kb.keyboard_start
        )
        await self.telegram.edit_message(edit)
        # self.fsm.set_state(callback.message.chat.id, State())

    

    