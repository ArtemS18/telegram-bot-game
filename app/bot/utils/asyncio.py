import asyncio
import typing

from app.store.tg_api.models import SendMessage

if typing.TYPE_CHECKING:
    from app.bot.states.models import BotStates
    from app.store.game.accessor import GameAccessor
    from app.web.app import Application


class AsyncioUtils:
    def __init__(self, app: "Application"):
        self.app = app
        self.telegram = app.store.tg_api
        self.answer_queues = app.bot.answer_queues

    async def wait_for_answer(self, chat_id) -> str:
            return await self.answer_queues[chat_id].get()
        
    async def send_5_seconds_warning(self, chat_id: int):
        time = 10
        await asyncio.sleep(60-time)
        warning = SendMessage(
            chat_id=chat_id,
            text=f"⏳ Осталось {time} секунд! Поторопитесь с ответом!",
        )
        await self.telegram.send_message(warning)


    async def start_timer_with_warning(self, chat_id: int) -> str:
        warning_task = asyncio.create_task(self.send_5_seconds_warning(chat_id))
        try:
            user_answer = await asyncio.wait_for(self.wait_for_answer(chat_id), timeout=60)
            return user_answer
        except asyncio.TimeoutError:
            raise
        finally:
            warning_task.cancel()
            try:
                await warning_task
            except asyncio.CancelledError:
                pass