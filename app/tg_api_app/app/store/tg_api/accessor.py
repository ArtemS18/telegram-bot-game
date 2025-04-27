import asyncio
import json
import logging
import typing
from urllib.parse import urlencode, urljoin

from aiohttp import ClientSession
import aio_pika  # Добавляем библиотеку для работы с RabbitMQ

from app.base.base_accessor import BaseAccessor
from .models import EditMessageText, SendMessage, Update
from .poller import Poller
from .schema import InlineKeyboardMarkupSchema, UpdateSchema, MessageSchema

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

        self.rabbit_connection: aio_pika.RobustConnection | None = None
        self.rabbit_channel: aio_pika.abc.AbstractChannel | None = None
        self.rabbit_exchange: aio_pika.Exchange | None = None

    async def connect(self, app: "Application") -> None:
        self.session = ClientSession()
        self.poller = Poller(self.app.store)
        await self.poller.start()

        # Соединение с RabbitMQ
        self.rabbit_connection = await aio_pika.connect_robust(
            self.app.config.rabbitmq.url,
        )
        self.rabbit_channel = await self.rabbit_connection.channel()
        self.rabbit_exchange = await self.rabbit_channel.declare_exchange(
            name="telegram_updates",
            type=aio_pika.ExchangeType.FANOUT,
            durable=True,
        )
        self.rabbit_queue = await self.rabbit_channel.declare_queue(
            "telegram_updates_queue",  # имя очереди
            durable=True,               # очередь устойчива к перезапускам RabbitMQ
        )

        # Привязка очереди к обмену
        await self.rabbit_queue.bind(self.rabbit_exchange)

        self.app.log.info("Start polling")

    async def disconnect(self, app: "Application") -> None:
        if self.poller and self.poller.is_running:
            await self.poller.stop()
        if self.session:
            await self.session.close()
        if self.rabbit_connection:
            await self.rabbit_connection.close()

    @staticmethod
    def _build_query(host: str, token: str, method: str, params: dict) -> str:
        url = f"{host}{token}/"
        return f"{urljoin(url, method)}?{urlencode(params)}"

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
            if results:
                for result in results:
                    logger.info(results)
                    self.offset = result["update_id"] + 1
                    await self._publish_update(result)

    async def _publish_update(self, update: dict) -> None:
        if not self.rabbit_exchange:
            logger.error("RabbitMQ exchange is not initialized")
            return
        message_body = json.dumps(update).encode()
        await self.rabbit_exchange.publish(
            aio_pika.Message(body=message_body),
            routing_key="telegram_updates_queue"
        )
        logger.info("Published update to RabbitMQ")
