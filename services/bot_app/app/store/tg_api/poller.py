import asyncio
import logging
from app.store import Store

logger = logging.getLogger(__name__)

class Consumer:
    def __init__(self, store: Store) -> None:
        self.store = store
        self.is_running = False
        self.customer_task: asyncio.Task | None = None

    async def start(self) -> None:
        if not self.is_running:
            self.is_running = True
            # Запуск задачи прослушивания
            self.customer_task = asyncio.create_task(self.listen())

    async def stop(self) -> None:
        if self.is_running:
            self.is_running = False
            if self.customer_task:
                await self.customer_task
                self.customer_task = None 

    async def listen(self) -> None:
        try:
            await self.store.tg_api.consume()  # Начало прослушивания очереди
        except Exception as e:
            logger.error(f"Error during message consumption: {e}")
        finally:
            logger.error(f"STOP")
            # Завершаем задачу, если она была успешно завершена
            if self.is_running:
                self.is_running = False
            self.customer_task = None  # Обнуляем задачу
