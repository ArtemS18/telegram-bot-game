from enum import Enum as PyEnum

class BotState(PyEnum):
    none = "NONE"
    creation_game = "WAIT_CREATION_GAME"
    add_users = "WAIT_ADD_USERS"
    start_game = "WAIT_START_GAME"
    select_capitan = "WAIT_SELECT_CAPITAN"
    question_active = "QUESTION_ACTIVE"
    check_answer = "CHECK_ANSWER"
    round_results = "ROUND_RESULTS"
    finish = "FINISH"