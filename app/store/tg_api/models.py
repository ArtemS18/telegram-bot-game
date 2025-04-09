from dataclasses import dataclass

@dataclass
class User:
    id: int

@dataclass
class Chat:
    chat_id : int

@dataclass
class Message:
    message_id: int
    from_user: User
    chat: Chat
    text: str
    