import logging
import typing
from urllib.parse import urlencode, urljoin

from aiohttp import ClientSession

from app.base.base_accessor import BaseAccessor

from .models import MessageDTO, Update
from .poller import Poller
from .schema import UpdateSchema

logger = logging.getLogger(__name__)


if typing.TYPE_CHECKING:
    from aiohttp.web import Application

API_URL = "https://api.telegram.org/bot"


class TgApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.poller: Poller | None = None
        self.offset: int = 0
        self.update_schema = UpdateSchema()
        
    async def connect(self, app: "Application"):
         self.session = ClientSession()
         self.poller = Poller(self.app.store)
         await self.poller.start()
         logger.info("Start polling")
         
    async def disconnect(self, app: "Application"):
        if self.poller.is_running():
            await self.poller.stop()

    @staticmethod 
    def _build_query(host: str, token: str, method: str, params: dict) -> str:
        url = f"{host}{token}/"
        return f"{urljoin(url, method)}?{urlencode(params)}"
    
    async def send_message(self, message: MessageDTO):
         async with self.session.post(
             self._build_query(
                host=API_URL,
                token=self.app.config.bot.token,
                method="sendMessage",
                params={"chat_id": message.chat_id, "text": message.text})
        ) as response:
             data = await response.json()
             logger.info(data)
    
    async def poll(self):
        async with self.session.get(
            self._build_query(
                host=API_URL,
                token=self.app.config.bot.token,
                method="getUpdates",
                params={"offset": self.offset, "timeout": 30})
        ) as response:
            data = await response.json()
            results = data.get("result", [])
            updates: Update = []
            if results:
                for result in results:
                    self.offset = result["update_id"] + 1
                    update = self.update_schema.load(result)
                    logger.info(data)
                    logger.info(update)
                    updates.append(update)
                await self.app.store.bot_manager.handle_updates(updates)


            


