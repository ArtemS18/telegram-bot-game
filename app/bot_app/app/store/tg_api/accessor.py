import asyncio
import json
import logging
import typing
import aio_pika
from urllib.parse import urlencode, urljoin

from aiohttp import ClientSession

from app.base.base_accessor import BaseAccessor

from .models import EditMessageText, SendMessage, Update
from .poller import Consumer
from .schema import InlineKeyboardMarkupSchema, UpdateSchema, MessageSchema

logger = logging.getLogger(__name__)


if typing.TYPE_CHECKING:
    from aiohttp.web import Application

API_URL = "https://api.telegram.org/bot"


class TgApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs) -> None:
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.poller: Consumer | None = None
        self.offset: int = 0
        self.update_schema = UpdateSchema()
        self.messageschema = MessageSchema()
        self.keyboard_schema = InlineKeyboardMarkupSchema()

        self.rabbit_connection: aio_pika.RobustConnection | None = None
        self.rabbit_channel: aio_pika.abc.AbstractChannel | None = None
        self.rabbit_exchange: aio_pika.Exchange | None = None

    async def connect(self, app: "Application") -> None:
        self.session = ClientSession()
        self.poller = Consumer(self.app.store)
        

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
        self.app.log.info("Rabbit_connection")
        await self.rabbit_queue.bind(self.rabbit_exchange)
        self.app.log.info("Start polling")
        await self.poller.start()
       


    async def disconnect(self, app: "Application") -> None:
        if self.poller.is_running:
            await self.poller.stop()
        if self.session:
            await self.session.close()
        if self.rabbit_connection:
            await self.rabbit_connection.close()
            logger.info("Disconnected from RabbitMQ")

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
            data =  await response.json()
            message = self.messageschema.load(data.get('result', {}))
            return message
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
            data =  await response.json()
            #message = self.messageschema.load(data.get('result', {}))
            #return message


    async def consume(self):
        async def on_message(message: aio_pika.IncomingMessage):
            async with message.process():
                logger.info(f"Received message: {message.body.decode()}")
                result = json.loads(message.body)
                update: Update = self.update_schema.load(result)
                update.type_query = list(result.keys())[1]
                await self.app.bot.manager.handle_updates(update)

        await self.rabbit_queue.consume(on_message)

        logger.info("Consumer started, waiting for messages...")
        await asyncio.Future()
