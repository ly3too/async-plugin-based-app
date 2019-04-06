import logging
from adispatch.channel import Channel
import asyncio as aio
from asyncio.events import AbstractEventLoop


class TestApp:
    """
        print message if main_config signal received
    """
    def __init__(self, loop: AbstractEventLoop, ch: Channel, logger: logging.Logger, *args, **kwargs):
        self._loop = loop
        self._ch = ch
        self._logger = logger
        logger.debug("config loader setup done")
        self._loop.run_until_complete(self._ch.sub("main_config", self.on_config_update))

    async def on_config_update(self, loop, signal, message, sender, *args, **kwargs):
        self._config = message
        self._logger.debug("received config: {}".format(self._config))

    async def on_setup_done(self):
        self._logger.debug("test app setup done")


def setup(*args, **kwargs):
    print("setup base")
    return TestApp(*args, **kwargs)
