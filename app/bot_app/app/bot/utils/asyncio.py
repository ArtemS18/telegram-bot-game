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
        self.ready_queues = app.bot.ready_queues
        self.active_tasks =  self.app.bot.active_tasks

    async def wait_get_team(self, chat_id) -> str:
            return await self.ready_queues[chat_id].get()

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

    async def start_timer_team(self, chat_id: int) -> str:
        try:
            self.app.log.info("START")
            team = await asyncio.wait_for(self.wait_get_team(chat_id), timeout=30)
            return team
        except asyncio.TimeoutError:
            raise 


    async def start_timer_with_warning(self, chat_id: int) -> str:
        warning_task = asyncio.create_task(self.send_5_seconds_warning(chat_id))
        if not self.app.bot.active_tasks.get(chat_id):
            self.app.bot.active_tasks[chat_id] = []

        self.app.bot.active_tasks[chat_id].append(warning_task)
        try:
            user_answer = await asyncio.wait_for(self.wait_for_answer(chat_id), timeout=60)
            return user_answer
        except asyncio.TimeoutError:
            raise 
        finally:
            warning_task.cancel()

    