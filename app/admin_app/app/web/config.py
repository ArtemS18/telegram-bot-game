import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application

@dataclass
class AdminConfig:
    email: str
    password: str


@dataclass
class DatabaseConfig:
    host: str
    port: int 
    user: str 
    password: str
    database: str 

@dataclass
class JWTConfig:
    access_tokem_expire_minutes: int
    secret_key: str
    algorithm: str

@dataclass
class Config:
    admin: AdminConfig = None
    database: DatabaseConfig = None
    jwt: JWTConfig = None

@dataclass
class EtcConfig:
    debug: bool = False
    web: dict = None
    sentry: dict = None
    store: dict = None


def setup_config(app: "Application", path: str):
    with open(path, "r") as f:
        raw_config = yaml.safe_load(f)

    app.config = Config(
        admin=AdminConfig(
            email=raw_config["admin"]["email"],
            password=raw_config["admin"]["password"],
        ),
        database=DatabaseConfig(**raw_config["database"]),

        jwt=JWTConfig(**raw_config["jwt"])
    )

def setup_etc_config(app: "Application", path: str):
    with open(path, "r", encoding="utf-8") as f:
        raw_etc = yaml.safe_load(f)
    app.etc_config = EtcConfig(
        debug=raw_etc.get("debug", False),
        web=raw_etc.get("web", {}),
        sentry=raw_etc.get("sentry", {}),
        store=raw_etc.get("store", {})
    )