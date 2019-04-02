from adispatch.dispatch import Dispatcher
import asyncio as aio


class Channel:
    def __init__(self, loop, parent_chan=None, ch_name = "/"):
        if not isinstance(ch_name, str) or (parent_chan != None and (len(ch_name) == 0 or ch_name[0] == "/")) or \
        (parent_chan == None and ch_name[0:1] != "/"):
            raise Exception("invalid arguments")
        ch_name = ch_name.strip("/")
        if ch_name.find("/") >= 0:
            raise Exception("invalid channel name")

        self._loop = loop
        self._sub_chan = dict()
        self._dispatcher = Dispatcher(loop)
        self._parent_chan = parent_chan
        if self._parent_chan is None:
            self._ch_name = "/"
        else:
            self._ch_name = ch_name

    async def sub(self, signal, callback):
        await self._dispatcher.sub(signal, callback)

    async def pub(self, signal, message = None, sender = None):
        loop = aio.get_event_loop()
        loop.create_task(self._dispatcher.pub(signal, message, sender))
        for k, ch in self._sub_chan.items():
            loop.create_task(ch.pub(signal, message, sender))

    def pub_threadsafe(self,signal, message = None, sender = None):
        self._dispatcher.pub_threadsafe(signal, message, sender)
        for k,ch in self._sub_chan:
            ch.pub_threadsafe(signal, message, sender)

    def get_sub_ch(self, ch_name: str, create=False):
        ch_name = ch_name.strip("/")
        if len(ch_name) == 0 or self._ch_name == ch_name:
            return self
        idx = ch_name.find("/")
        if (idx < 0):
            cur_ch = ch_name
        else:
            cur_ch = ch_name[0:idx]
        if cur_ch not in self._sub_chan:
            if not create:
                return None
            self._sub_chan[cur_ch] = Channel(self._loop, self, cur_ch)
        return self._sub_chan[cur_ch].get_sub_ch(ch_name[idx + 1:], create)

    def get_or_create_sub_ch(self, ch_name: str):
        return self.get_sub_ch(ch_name, create=True)

    def get_ch_name(self):
        if self._parent_chan == None:
            return self._ch_name
        par_name = self._parent_chan.get_ch_name()
        if par_name == "/":
            return par_name + self._ch_name
        return par_name + "/" + self._ch_name
