from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class User:
    id: int
    count_wins: int = 0
    count_losses: int = 0
    is_admin: bool = False


@dataclass
class Chat:
    id: int
    bot_state: str


@dataclass
class Game:
    id: int
    chat_id: int
    score_gamers: int = 0
    score_bot: int = 0
    round: int = 0
    status: Literal["in_progress", "end"] = "in_progress"
    winner: Literal["users", "bot", "not_defined"] = "not_defined"


@dataclass
class GameUser:
    id: int
    game_id: int
    user_id: int
    game_role: Literal["player", "capitan"]


@dataclass
class Question:
    id: int
    question_text: str
    answer_text: str
    img_url: Optional[str] = None


@dataclass
class GameQuestion:
    id: int
    question_id: int
    status: Literal["in_progress", "correct_answer", "wrong_answer"]
    answering_player: int
