import logging
from adispatch.channel import Channel
import asyncio as aio
from asyncio.events import AbstractEventLoop

class ConfigLoader:
    def __init__(self, loop:AbstractEventLoop, ch: Channel, logger: logging.Logger, *args, **kwargs):
        self._loop = loop
        self._ch = ch
        self._logger = logger
        logger.debug("config loader setup done")

    async def pub_config(self):
        while True:
            await aio.sleep(2)
            await self._ch.pub("main_config", {"test_config":"config"}, type(self).__name__)

    async def on_setup_done(self):
        await self._ch.pub("main_config", {"test_config":"config"}, type(self).__name__)
        self._loop.create_task(self.pub_config())


def setup(*args, **kwargs):
    print("setup base")
    return ConfigLoader(*args, **kwargs)
