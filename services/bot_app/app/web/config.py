import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass
class BotConfig:
    token: str


@dataclass
class DatabaseConfig:
    host: str
    port: int 
    user: str 
    password: str
    database: str 

@dataclass
class RabbitMQConfig:
    url: str


@dataclass
class Config:
    bot: BotConfig = None
    database: DatabaseConfig = None
    rabbitmq: RabbitMQConfig = None


def setup_config(app: "Application", path: str):
    with open(path, "r") as f:
        raw_config = yaml.safe_load(f)

    app.config = Config(

        bot=BotConfig(
            token=raw_config["bot"]["token"],
        ),
        database=DatabaseConfig(**raw_config["database"]),
        rabbitmq=RabbitMQConfig(url="amqp://guest:guest@rabbitmq/")

    )
