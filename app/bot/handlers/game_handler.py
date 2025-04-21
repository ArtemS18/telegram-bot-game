import asyncio
import typing

from app.store.tg_api.models import Message, SendMessage

if typing.TYPE_CHECKING:
    from app.bot.states.models import BotStates
    from app.bot.states.state_manager import FSM
    from app.store.game.accessor import GameAccessor
    from app.store.tg_api.accessor import TgApiAccessor
    from app.web.app import Application


class GameHandler:
    def __init__(self, app: "Application"):
        self.app: "Application" = app
        self.fsm: "FSM" = app.bot.fsm
        self.telegram: "TgApiAccessor" = app.store.tg_api
        self.db: "GameAccessor" = app.store.game
        self.states: "BotStates" = app.bot.states
        self.answer_queues = app.bot.answer_queues

    async def start_game_round(self, message: Message):
        chat_id = message.chat.id
        round_number = 1

        answer = SendMessage(
            chat_id=chat_id,
            text=f"Раунд №{round_number} начался! Внимание, вопрос:",
        )
        await self.telegram.send_message(answer)
        await asyncio.sleep(3)

        question = await self.db.get_random_question()
        if not question:
            await self.end_game(
                chat_id, 
                "Вопросы закончились. Игра завершена!"
            )
            return

        question_message = SendMessage(
            chat_id=chat_id,
            text=f"{question.question_text}\n\n{question.img_url or ''}",
        )
        await self.telegram.send_message(question_message)
        self.fsm.set_state(chat_id, self.states.check_answer)

        try:
            user_answer = await asyncio.wait_for(
                self.wait_for_answer(chat_id), timeout=30
            )
            if user_answer.lower() == question.answer_text.lower():
                response = "Правильно! Вы дали верный ответ."
            else:
                response = f'''
                Неправильно! 
                Правильный ответ: {question.answer_text}'''

        except asyncio.TimeoutError:
            response = f'''
            Время вышло! 
            Правильный ответ: {question.answer_text}'''

        result_message = SendMessage(
            chat_id=chat_id,
            text=response,
        )
        await self.telegram.send_message(result_message)
        await asyncio.sleep(3)
        self.fsm.set_state(chat_id, self.states.question_active)

    async def end_game(self, chat_id: int, message: str):
        answer = SendMessage(
            chat_id=chat_id,
            text=message,
        )
        await self.telegram.send_message(answer)

        self.fsm.set_state(chat_id, None)

    async def wait_for_answer(self, chat_id) -> str:
        return await self.answer_queues[chat_id].get()
