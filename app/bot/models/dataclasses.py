from dataclasses import dataclass
from typing import Literal, Optional

from app.game.models.play import User


@dataclass
class Answer:
    user_id: int
    chat_id: int
    text: str | None = None
