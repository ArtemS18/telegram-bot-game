import typing

if typing.TYPE_CHECKING:
    from aiohttp.web import Application

class BaseAccessor():
    def __init__(self, app: "Application", *args, **kwargs):
        self.app = app

        app.on_startup.append(self.connect)
        app.on_cleanup.append(self.disconnect)

    async def connect(self, app: "Application"):
        pass
    async def disconnect(self, app: "Application"):
        pass


