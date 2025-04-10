import typing

from app.store.tg_api.models import (
    MessageDTO,
    Update,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app

    async def handle_updates(self, updates: list[Update]):
        """Обрабатывает список обновлений, полученных от TG API."""
        for update in updates:
            if update.message.text:
                message = update.message
                chat_id = message.chat.id
                incoming_message_text = message.text

                if incoming_message_text.strip():
                    response_message_text = incoming_message_text
                    message = MessageDTO(chat_id=chat_id, 
                                         text=response_message_text)
                    await self.app.store.tg_api.send_message(message)