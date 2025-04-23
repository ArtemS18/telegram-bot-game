import typing

if typing.TYPE_CHECKING:
    from aiohttp.web import Application


class BaseAccessor:
    def __init__(self, app: "Application", *args, **kwargs):
        self.app = app

        app.add_event_handler("startup", self.connect)
        app.add_event_handler("shutdown", self.disconnect)

    async def connect(self):
        pass

    async def disconnect(self):
        pass
