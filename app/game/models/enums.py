from enum import Enum as PyEnum


class GameRole(PyEnum):
    player = "player"
    capitan = "capitan"


class GameStatus(PyEnum):
    in_progress = "in_progress"
    end = "end"


class WinnerType(PyEnum):
    users = "users"
    bot = "bot"
    not_defined = "not_defined"


class QuestionStatus(PyEnum):
    in_progress = "in_progress"
    correct_answer = "correct_answer"
    wrong_answer = "wrong_answer"

