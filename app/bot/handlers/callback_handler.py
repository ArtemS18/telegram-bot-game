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
        print("_____",callback.message)
        if not await self.db.add_user_to_game(callback.message.from_user.id, callback.message.chat.id):
            last_text = callback.message.text
            new_text = f"{last_text} \n @{callback.message.from_user.username}"
            edit = EditMessageText(
                chat_id=callback.message.chat.id, 
                message_id=callback.message.message_id,
                text=new_text,
                reply_markup=kb.keyboard_start
            )
            await self.telegram.edit_message(edit)
        # self.fsm.set_state(callback.message.chat.id, State())

    

    