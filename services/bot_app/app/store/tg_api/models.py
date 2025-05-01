from dataclasses import dataclass
from typing import List


@dataclass
class User:
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None


@dataclass
class Chat:
    id: int
    title: str | None = None


@dataclass
class Message:
    message_id: int
    from_user: User
    date: int
    chat: Chat
    text: str | None = None


@dataclass
class InlineQuery:
    id: int
    from_user: User
    query: str
    offset: str


@dataclass
class CallbackQuery:
    id: int
    from_user: User
    data: str
    message: Message | None = None


@dataclass
class Update:
    update_id: int
    type_query: str | None = None
    message: Message | None = None
    inline_query: InlineQuery | None = None
    callback_query: CallbackQuery | None = None


@dataclass
class InlineKeyboardButton:
    text: str
    url: str | None = None
    callback_data: str | None = None


@dataclass
class InlineKeyboardMarkup:
    inline_keyboard: List[List[InlineKeyboardButton]]


@dataclass
class SendMessage:
    chat_id: str
    text: str
    reply_markup: InlineKeyboardMarkup | None = None


@dataclass
class EditMessageText:
    chat_id: int
    message_id: int
    text: str
    inline_message_id: str | None = None
    reply_markup: InlineKeyboardMarkup | None = None
