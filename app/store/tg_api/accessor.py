import logging
import typing

from aiohttp import ClientSession

from app.base.base_accessor import BaseAccessor

from .poller import Poller

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if typing.TYPE_CHECKING:
    from aiohttp.web import Application

BOT_TOKEN = "7566227447:AAFDnW0FaxerLK2VvZn-XiDhyltkwbQE2kg"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"


class TgApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.poller: Poller | None = None
        self.offset = -1
        
    async def connect(self, app: "Application"):
         self.session = ClientSession()
         self.poller = Poller(self.app.store)
         await self.poller.start()
        
    async def disconnect(self, app: "Application"):
        await self.poller.stop()
        return await super().disconnect(app)
    
    async def poll(self):
        url = API_URL + "getUpdates"
        async with self.session.get(
                url,
                params={"offset": self.offset, "timeout": 10})as response:
            data = await response.json()
            logger.info(data)

            # await self.app.store.bots_manager.handle_updates(updates)


