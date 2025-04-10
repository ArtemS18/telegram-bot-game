from dataclasses import dataclass


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
    text: str


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
    message: Message | None
    data: str


@dataclass
class Update:
    update_id: int
    message: Message | None = None
    inline_query: InlineQuery | None = None
    callback_query: CallbackQuery | None = None


@dataclass
class MessageDTO:
    chat_id: str 
    text: str