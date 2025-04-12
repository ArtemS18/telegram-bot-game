from unittest.mock import AsyncMock

import pytest

from app.store.bot.manager import BotManager
from app.store.tg_api.models import Chat, Message, SendMessage, Update, User


@pytest.fixture
def bot_manager():
    app = AsyncMock()
    app.store.tg_api.send_message = AsyncMock() 
    return BotManager(app)


@pytest.mark.asyncio
async def test_start_command(bot_manager):
    """Тест команды /start."""
    update = Update(
        update_id=1,
        message=Message(
            message_id=1,
            from_user=User(id=123, first_name="Test", username="test_user"),
            date=1234567890,
            chat=Chat(id=123, title="Test Chat"),
            text="/start",
        ),
    )
    await bot_manager.handle_updates([update])

    bot_manager.app.store.tg_api.send_message.assert_called_once_with(
        SendMessage(chat_id=123, text="Привет давай поиграем в Игру....")
    )
