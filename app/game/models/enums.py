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


class BotState(PyEnum):
    creation_game = "WAIT_CREATION_GAME"
    add_users = "WAIT_ADD_USERS"
    start_game = "WAIT_START_GAME"
    select_capitan = "WAIT_SELECT_CAPITAN"
    question_active = "QUESTION_ACTIVE"
    check_answer = "CHECK_ANSWER"
    round_results = "ROUND_RESULTS"
    finish = "FINISH"
