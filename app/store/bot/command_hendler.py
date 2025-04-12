import typing

from app.store.tg_api.models import (
    Message,
    SendMessage,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application


class CommandHandler:
    def __init__(self, app: "Application"):
        self.app = app

    async def start_command(self, message: Message):
        message_dto = SendMessage(
                        chat_id=message.chat.id, 
                        text="Привет давай поиграем в Игру...."
                    )
        await self.app.store.tg_api.send_message(message_dto)

    async def add_user(self, message: Message):
        message_dto = SendMessage(
                        chat_id=message.chat.id, 
                        text="Начнем набор игроков"
                    )
        await self.app.store.tg_api.send_message(message_dto)