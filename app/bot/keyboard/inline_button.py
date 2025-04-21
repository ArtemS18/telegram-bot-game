from app.store.tg_api.models import InlineKeyboardButton, InlineKeyboardMarkup

keyboard_add = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(
            text="Присоединиться",
            callback_data="join")],
    ]
)

keyboard_start = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(text="Старт!", callback_data="start")],
    ]
)

keyboard_select = InlineKeyboardMarkup(
    [
        # [InlineKeyboardButton(text="Присоединиться", callback_data="join")]
        [InlineKeyboardButton(
            text="Выбрать капитана",
            callback_data="select")],
    ]
)
