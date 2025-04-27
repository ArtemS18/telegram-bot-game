from app.store.tg_api.models import InlineKeyboardButton, InlineKeyboardMarkup

keyboard_add = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(
            text="Присоединиться",
            callback_data="join")],
        [InlineKeyboardButton(
            text="Выйти",
            callback_data="quite")],
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
            text="Покинуть игру",
            callback_data="userquite")],
    ]
)

keyboard_get = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(
            text="Дать ответ",
            callback_data="get")],
    ]
)

