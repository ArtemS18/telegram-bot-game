import json
import logging
import typing
from urllib.parse import urlencode, urljoin

from aiohttp import ClientSession

from app.base.base_accessor import BaseAccessor

from .models import EditMessageText, SendMessage, Update
from .poller import Poller
from .schema import InlineKeyboardMarkupSchema, UpdateSchema

logger = logging.getLogger(__name__)


if typing.TYPE_CHECKING:
    from aiohttp.web import Application

API_URL = "https://api.telegram.org/bot"


class TgApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs) -> None:
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.poller: Poller | None = None
        self.offset: int = 0
        self.update_schema = UpdateSchema()
        self.keyboard_schema = InlineKeyboardMarkupSchema()

    async def connect(self) -> None:
        self.session = ClientSession()
        self.poller = Poller(self.app.store)
        await self.poller.start()
        self.app.log.info("Start polling")

    async def disconnect(self) -> None:
        if self.poller.is_running:
            await self.poller.stop()
        if self.session:
            await self.session.close()

    @staticmethod
    def _get_params() -> dict:
        pass

    @staticmethod
    def _build_query(host: str, token: str, method: str, params: dict) -> str:
        url = f"{host}{token}/"
        return f"{urljoin(url, method)}?{urlencode(params)}"

    async def send_message(self, message: SendMessage) -> None:
        params = {"chat_id": message.chat_id, "text": message.text}

        if message.reply_markup is not None:
            params["reply_markup"] = json.dumps(
                self.keyboard_schema.dump(message.reply_markup)
            )

        async with self.session.post(
            self._build_query(
                host=API_URL,
                token=self.app.config.bot.token,
                method="sendMessage",
                params=params,
            )
        ) as response:
            await response.json()
            # data = await response.json()
            # logger.info(data)

    async def edit_message(self, message: EditMessageText) -> None:
        params = {
            "chat_id": message.chat_id,
            "text": message.text,
            "message_id": message.message_id,
        }

        if message.reply_markup is not None:
            params["reply_markup"] = json.dumps(
                self.keyboard_schema.dump(message.reply_markup)
            )

        async with self.session.post(
            self._build_query(
                host=API_URL,
                token=self.app.config.bot.token,
                method="editMessageText",
                params=params,
            )
        ) as response:
            data = await response.json()
            logger.info(data)

    async def get_long_poll(self) -> None:
        async with self.session.get(
            self._build_query(
                host=API_URL,
                token=self.app.config.bot.token,
                method="getUpdates",
                params={"offset": self.offset, "timeout": 10},
            )
        ) as response:
            data = await response.json()
            results = data.get("result", [])
            updates: list[Update] = []
            if results:
                for result in results:
                    # logger.info(results)
                    self.offset = result["update_id"] + 1
                    update: Update = self.update_schema.load(result)
                    update.type_query = list(result.keys())[1]
                    updates.append(update)
                return update

    async def long_poll(self) -> None:
        async with self.session.get(
            self._build_query(
                host=API_URL,
                token=self.app.config.bot.token,
                method="getUpdates",
                params={"offset": self.offset, "timeout": 30},
            )
        ) as response:
            data = await response.json()
            results = data.get("result", [])
            updates: list[Update] = []
            if results:
                for result in results:
                    # logger.info(results)
                    self.offset = result["update_id"] + 1
                    update: Update = self.update_schema.load(result)
                    update.type_query = list(result.keys())[1]
                    updates.append(update)
                await self.app.bot.manager.handle_updates(updates)
