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
        [InlineKeyboardButton(
            text="Выбрать капитана",
            callback_data="select")],
    ]
)

keyboard_next = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(
            text="Продолжить играть",
            callback_data="next")],
        [InlineKeyboardButton(
            text="Выйти из игры",
            callback_data="quite")],
    ]
)

