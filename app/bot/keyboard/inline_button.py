from app.store.tg_api.models import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

buttons_start = [
            [InlineKeyboardButton(text="Присоединиться", callback_data="join")],
        ]
keyboard_start = InlineKeyboardMarkup(inline_keyboard=buttons_start)