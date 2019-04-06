import asyncio as aio
from asyncio.events import AbstractEventLoop


class Dispatcher:
    """
        provide async pub-sub functionality

        any callback will be put into event loop, if subbed signal is fired
        callback must have a interface like cb(loop, signal, message, sender)
    """

    def __init__(self, loop: AbstractEventLoop):
        self._loop = loop
        self._cbs = dict()

    async def sub(self, signal, callback):
        """
        sub to a signal
        :param str signal:
        :param callback:
        :return:
        """
        if signal not in self._cbs:
            self._cbs[signal] = set()
        self._cbs[signal].add(callback)

    async def unsub(self, signal, callback):
        if signal not in self._cbs:
            return
        self._cbs[signal].remove(callback)

    def _pub(self, signal, message = None, sender = None, thread_safe = False):
        if signal not in self._cbs:
            return 0

        cnt = 0
        for cb in self._cbs[signal]:
            if aio.iscoroutinefunction(cb):
                if thread_safe:
                    aio.run_coroutine_threadsafe(cb(self._loop, signal, message, sender), loop=self._loop)
                else:
                    aio.ensure_future(cb(self._loop, signal, message, sender), loop=self._loop)
            else:
                if thread_safe:
                    self._loop.call_soon_threadsafe(cb, self._loop, signal, message, sender)
                else:
                    self._loop.call_soon(cb, self._loop, signal, message, sender)
            cnt += 1
        return cnt

    async def pub(self, signal, message = None, sender = None, *args, **kwargs):
        kwargs["thread_safe"] = False
        return self._pub(signal, message, sender, *args, **kwargs)

    def pub_threadsafe(self, signal, message = None, sender = None, *args, **kwargs):
        kwargs["thread_safe"] = True
        return self._pub(signal, message, sender, *args, **kwargs)

