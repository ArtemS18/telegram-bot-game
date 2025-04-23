import asyncio
import typing

from app.bot.keyboard import inline_button as kb
from app.bot.models.dataclasses import Answer
from app.game.models.enums import GameRole, GameStatus, QuestionStatus, WinnerType
from app.game.models.play import Game
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
        self.asyncio = app.bot.utils.asyncio

    async def start_game_round(self, chat_id: int) -> None:
        game: Game = await self.db.get_game_by_chat_id(chat_id)
        capitan = await self.db.get_capitan_by_game_id(game.id)

        await self.telegram.send_message(
            SendMessage(
                chat_id=chat_id,
                text=f"Раунд №{game.round + 1} начался! Внимание, вопрос:"
            )
        )

        await asyncio.sleep(3)

        question = await self.db.get_random_question(chat_id)
        if not question:
            await self.end_game(
                SendMessage(
                    chat_id=chat_id,
                    text="🛑 Вопросы закончились. Игра завершена!"
                )
            )
            return

        game_question = await self.db.create_gamequestion_by_chat_id(
            chat_id, question.id, capitan.id
        )

        await self.telegram.send_message(
            SendMessage(
                chat_id=chat_id,
                text=f"Вопрос: {question.question_text} (60 секунд на обсуждение)\n\n{question.img_url or ''} ",
            )
        )

        self.fsm.set_state(chat_id, self.states.check_answer)

        try:
            answer: Answer = await self.asyncio.start_timer_with_warning(chat_id)
            if answer.text.lower() == question.answer_text.lower():
                response = "✅ Правильно! Вы дали верный ответ."
                game.score_gamers += 1
                game_question.status = QuestionStatus.correct_answer
            else:
                response = f"❌ Неправильно!\nПравильный ответ: {question.answer_text}"
                game.score_bot += 1
                game_question.status = QuestionStatus.wrong_answer
        except asyncio.TimeoutError:
            response = f"⏰ Время вышло! Правильный ответ: {question.answer_text}"
            game.score_bot += 1
            game_question.status = QuestionStatus.wrong_answer
        finally:
            game.round += 1
            await self.db.update_object(game)
            await self.db.update_object(game_question)

        await self.telegram.send_message(
            SendMessage(
                chat_id=chat_id,
                text=response,
            )
        )

        await asyncio.sleep(3)

        self.fsm.set_state(chat_id, self.states.round_results)
        await self.round_results(chat_id, game)

    async def round_results(self, chat_id: int, game: Game) -> None:
        text = f"Счёт: {game.score_gamers}:{game.score_bot} \n\n"

        if game.round < 2:
            if game.score_gamers > game.score_bot:
                text += " 🏆 В пользу знатоков!"
            elif game.score_gamers < game.score_bot:
                text += " 🏆 В пользу телезрителей!"
            else:
                text += " 🤝 Пока ничья!"

            text += "\n\n⏳ Следующий раунд начнется через 5 секунд!"

            await self.telegram.send_message(
                SendMessage(
                    chat_id=chat_id,
                    text=text,
                )
            )

            await asyncio.sleep(5)
            await self.start_game_round(chat_id)
        else:
            self.fsm.set_state(chat_id, self.states.finish)
            await self.finish_game(chat_id, game)

    async def finish_game(self, chat_id: int, game: Game) -> None:
        score_text = f"Счёт: {game.score_gamers}:{game.score_bot} 🎮"

        if game.score_gamers > game.score_bot:
            result_text = "🎉 Победили знатоки!"
            game.winner = WinnerType.users
        elif game.score_gamers < game.score_bot:
            result_text = "🎉 Победили телезрители!"
            game.winner = WinnerType.bot
        else:
            result_text = "🤝 Ничья!"
            game.winner = WinnerType.not_defined

        await self.telegram.send_message(
            SendMessage(chat_id=chat_id, text=score_text)
        )

        await asyncio.sleep(3)

        await self.telegram.send_message(
            SendMessage(chat_id=chat_id, text=result_text)
        )

        await asyncio.sleep(3)

        await self.end_game(
            SendMessage(
                chat_id=chat_id,
                text="Спасибо за игру!\nНажмите на кнопку для начала новой игры! 🎮",
                reply_markup=kb.keyboard_next,
            )
        )

    async def end_game(self, send_message: SendMessage) -> None:
        game: Game = await self.db.get_game_by_chat_id(send_message.chat_id)

        await self.telegram.send_message(send_message)
        await self.db.update_game(game.id, status=GameStatus.end)
