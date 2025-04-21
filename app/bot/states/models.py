from dataclasses import dataclass


@dataclass
class State:
    name: str | None = None


@dataclass
class BotStates:
    creation_game = State("WAIT_CREATION_GAME")
    add_users = State("WAIT_ADD_USERS")
    select_capitan = State("WAIT_SELECT_CAPITAN")
    start_game = State("WAIT_START_GAME")
    question_active = State("QUESTION_ACTIVE")
    check_answer = State("CHECK_ANSWER")
    round_results = State("ROUND_RESULTS")
    finish = State("FINISH")
