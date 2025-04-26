from typing import List

from sqlalchemy import VARCHAR, BigInteger, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.base_sqlalchemy import BaseModel

from .enums import BotState, GameRole, GameStatus, QuestionStatus, WinnerType


class Game(BaseModel):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    score_gamers: Mapped[int] = mapped_column(default=0)
    score_bot: Mapped[int] = mapped_column(default=0)
    round: Mapped[int] = mapped_column(default=0)
    status: Mapped[GameStatus] = mapped_column(
        Enum(GameStatus), default=GameStatus.in_progress
    )
    winner: Mapped[WinnerType] = mapped_column(
        Enum(WinnerType), default=WinnerType.not_defined
    )

    players: Mapped[List["GameUser"]] = relationship(back_populates="game")
    questions: Mapped[List["GameQuestion"]] = relationship(back_populates="game")
    chat: Mapped["Chat"] = relationship(back_populates="games")


class GameUser(BaseModel):
    __tablename__ = "games_users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    game_role: Mapped[GameRole] = mapped_column(Enum(GameRole), default=GameRole.player)

    game: Mapped["Game"] = relationship(back_populates="players")
    user: Mapped["User"] = relationship(back_populates="games")
    answered_questions: Mapped[List["GameQuestion"]] = relationship(
        back_populates="player"
    )


class Question(BaseModel):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_text: Mapped[str] = mapped_column(Text)
    answer_text: Mapped[str] = mapped_column(Text)
    img_url: Mapped[str | None] = mapped_column(VARCHAR(255), nullable=True)

    game_questions: Mapped[List["GameQuestion"]] = relationship(
        back_populates="question"
    )


class GameQuestion(BaseModel):
    __tablename__ = "games_questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    status: Mapped[QuestionStatus] = mapped_column(
        Enum(QuestionStatus), default=QuestionStatus.in_progress
    )
    answering_player: Mapped[int] = mapped_column(ForeignKey("games_users.id"), nullable=True)

    game: Mapped["Game"] = relationship(back_populates="questions")
    question: Mapped["Question"] = relationship(back_populates="game_questions")
    player: Mapped["GameUser"] = relationship(back_populates="answered_questions")


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(VARCHAR(255))
    count_wins: Mapped[int] = mapped_column(default=0)
    count_losses: Mapped[int] = mapped_column(default=0)
    is_admin: Mapped[bool] = mapped_column(default=False)

    games: Mapped[List["GameUser"]] = relationship(back_populates="user")


class Chat(BaseModel):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    bot_state: Mapped[BotState] = mapped_column(
        Enum(BotState), default=BotState.creation_game
    )

    games: Mapped[List["Game"]] = relationship(back_populates="chat")
