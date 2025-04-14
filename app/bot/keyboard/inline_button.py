from app.store.tg_api.models import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

buttons_start = [
            [InlineKeyboardButton(text="Начать игру", callback_data="start_game")],
            [InlineKeyboardButton(text="Помощь", callback_data="help")],
        ]
keyboard_start = InlineKeyboardMarkup(inline_keyboard=buttons_start)