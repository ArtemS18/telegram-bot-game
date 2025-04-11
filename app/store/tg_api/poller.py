import asyncio
import logging

from app.store import Store

logger = logging.getLogger(__name__)


class Poller:
    def __init__(self, store: Store) -> None:
        self.store = store
        self.is_running = False
        self.poll_task: asyncio.Task | None = None

    async def start(self) -> None:
        if not self.is_running:
            self.is_running = True
            self.poll_task = asyncio.create_task(self.poll())

    async def stop(self) -> None:
        if self.is_running:
            self.is_running = False
            if self.poll_task:
                await self.poll_task

    async def poll(self) -> None:
        try:
            while self.is_running:
                await self.store.tg_api.poll()
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(e)
            self.is_running = False
        finally:
            if self.poll_task:
                self.poll_task = None
