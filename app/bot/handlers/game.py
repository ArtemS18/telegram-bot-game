import asyncio
import typing

from app.bot.keyboard import inline_button as kb
from app.bot.models.dataclasses import Answer
from app.game.models.enums import GameRole, GameStatus, QuestionStatus, WinnerType
from app.game.models.play import Game
from app.store.tg_api.models import EditMessageText, Message, SendMessage

if typing.TYPE_CHECKING:
    from app.bot.states.models import BotState
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
        self.states: "BotState" = app.bot.states
        self.answer_queues = app.bot.answer_queues
        self.asyncio = app.bot.utils.asyncio
        self.active_tasks =  self.app.bot.active_tasks

    async def start_round(self, message: Message) -> None:
        chat_id = message.chat.id
        game: Game = await self.db.get_game_by_chat_id(chat_id)
        capitan = await self.db.get_capitan_by_game_id(game.id)
        edit_message = await self.telegram.send_message(
            SendMessage(
                chat_id=chat_id,
                text=f"Раунд №{game.round + 1} начался! Внимание, вопрос:"
            )
        )

        question = await self.db.get_current_question(chat_id)
        if not question:
            question = await self.db.get_random_question(chat_id)
            await self.db.create_gamequestion_by_chat_id(chat_id, question.id, capitan.id)
        
        if not question:
            await self.db.update_game(game.id, status=GameStatus.end)
            await self.end_game(
                SendMessage(
                    chat_id=chat_id,
                    text="🛑 Вопросы закончились. Игра завершена!"
                )
            )
            return
        await asyncio.sleep(3)

        await self.telegram.edit_message(
            EditMessageText(
                chat_id=chat_id,
                message_id=edit_message.message_id,
                text=f"Вопрос: {question.question_text} (60 секунд на обсуждение)\n\n{question.img_url or ''} ",
                reply_markup=kb.keyboard_get
            )
        )

        await self.fsm.set_state(chat_id, self.states.select_answering)
        await self.process_answer(message)

    async def process_answer(self, message: Message) -> None:
        chat_id = message.chat.id
        game: Game = await self.db.get_game_by_chat_id(chat_id)
        question = await self.db.get_current_question(chat_id)
        response = "Попробуйте еще раз"
        game_question = await self.db.get_current_gamequestion(chat_id)

        try:
            answer: Answer = await self.asyncio.start_timer_with_warning(chat_id)
            if answer.text.lower() == question.answer_text.lower():
                response = "✅ Правильно! Вы дали верный ответ."
                game.score_gamers += 1
                game_question.status = QuestionStatus.correct_answer
                await self.db.update_game(game.id, score_gamers=game.score_gamers)
            else:
                response = f"❌ Неправильно!\nПравильный ответ: {question.answer_text}"
                game.score_bot += 1
                await self.db.update_game(game.id, score_bot=game.score_bot)
                game_question.status = QuestionStatus.wrong_answer
        except asyncio.TimeoutError:
            response = f"⏰ Время вышло! Правильный ответ: {question.answer_text}"
            game.score_bot += 1
            await self.db.update_game(game.id, score_bot=game.score_bot)
            game_question.status = QuestionStatus.wrong_answer
        finally:
            await self.db.update_object(game_question)

        new_message = await self.telegram.send_message(
            SendMessage(
                chat_id=chat_id,
                text=response,
            )
        )
        await self.fsm.set_state(chat_id, self.states.round_results)
        await self.round_results(new_message)

    async def round_results(self, message: Message) -> None:
        chat_id = message.chat.id
        game: Game = await self.db.get_game_by_chat_id(chat_id)
        text = f"Счёт: {game.score_gamers}:{game.score_bot} \n\n"

        if game.round < 2:
            if game.score_gamers > game.score_bot:
                text += " 🏆 В пользу знатоков!"
            elif game.score_gamers < game.score_bot:
                text += " 🏆 В пользу телезрителей!"
            else:
                text += " 🤝 Пока ничья!"

            text += "\n\n⏳ Следующий раунд начнется через 3 секунды!"
            await self.telegram.send_message(
                SendMessage(
                    chat_id=chat_id,
                    text=text,
                )
            )

            await self.db.update_game(game.id, round=game.round + 1)
            await self.start_round(message)
        else:
            await self.fsm.set_state(chat_id, self.states.finish)
            await self.finish_game(message)

    async def finish_game(self, message: Message) -> None:
        chat_id = message.chat.id
        game: Game = await self.db.get_game_by_chat_id(chat_id)
        score_text = f"Финальный счёт: {game.score_gamers}:{game.score_bot} \n\n"

        if game.score_gamers > game.score_bot:
            result_text = "🎉 Победили знатоки!"
            await self.db.update_game(game.id, winner=WinnerType.users)
        elif game.score_gamers < game.score_bot:
            result_text = "🎉 Победили телезрители!"
            await self.db.update_game(game.id, winner=WinnerType.bot)
        else:
            result_text = "🤝 Ничья!"
            await self.db.update_game(game.id, winner=WinnerType.not_defined)

        await self.telegram.send_message(
            SendMessage(chat_id=chat_id, text=score_text+result_text)
        )

        await self.db.update_game(game.id, status=GameStatus.end)
        await self.fsm.set_state(chat_id, self.states.lobbi)
        await self.end_game(
            SendMessage(
                chat_id=chat_id,
                text="Спасибо за игру!\nНажмите на кнопку для начала новой игры! 🎮",
                reply_markup=kb.keyboard_next,
            )
        )

    async def end_game(self, send_message: SendMessage) -> None:
        await self.telegram.send_message(send_message)
        
