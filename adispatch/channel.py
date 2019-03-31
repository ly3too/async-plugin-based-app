from adispatch.dispatch import Dispatcher


class Channel:
    def __init__(self, loop, parent_chan=None, ch_name = "/"):
        if not isinstance(ch_name, str) or (parent_chan != None and (len(ch_name) == 0 or ch_name[0] == "/")) or \
        (parent_chan == None and ch_name[0:1] != "/"):
            raise Exception("invalid arguments")
        ch_name = ch_name.strip("/")
        idx = ch_name.find("/")
        self._loop = loop
        self._sub_chan = dict()
        self._dispatcher = Dispatcher(loop)
        self._parent_chan = parent_chan
        if self._parent_chan == None:
            self._ch_name = "/"
            if (idx > 0):
                self._sub_chan[ch_name[0:idx]] = Channel(self._loop, self, ch_name)
        else:
            self._ch_name = ch_name[0:idx]
            if (len(ch_name[idx+1:]) != 0):
                self._sub_chan[ch_name[idx+1:]] = Channel(self._loop, self, ch_name[idx+1:])

    async def sub(self, signal, callback):
        await self._dispatcher.sub(signal, callback)

    async def pub(self, signal, message = None, sender = None):
        await self._dispatcher.pub(signal, message, sender)
        for k,ch in self._sub_chan:
            await ch.pub(signal, message, sender)

    def pub_threadsafe(self,signal, message = None, sender = None):
        self._dispatcher.pub_threadsafe(signal, message, sender)
        for k,ch in self._sub_chan:
            ch.pub_threadsafe(signal, message, sender)

    def get_chan(self, ch_name: str):
        ch_name = ch_name.strip("/")
        if len(ch_name) == 0:
            return self
        idx = ch_name.find("/")
        cur_ch = ch_name[0:idx]
        if cur_ch in self._sub_chan:
            return self._sub_chan[cur_ch].get_chan(ch_name[idx+1:])
        return None

    def get_or_create_ch(self, ch_name: str):
        ch_name = ch_name.strip("/")
        if len(ch_name) == 0:
            return self
        idx = ch_name.find("/")
        cur_ch = ch_name[0:idx]
        if cur_ch not in self._sub_chan:
            self._sub_chan[cur_ch] = Channel(self._loop, self, cur_ch)
        return self._sub_chan[cur_ch].get_or_create_ch(ch_name[idx+1:])

    def get_ch_name(self):
        if self._parent_chan == None:
            return self._ch_name
        par_name = self._parent_chan.get_ch_name()
        if par_name == "/":
            return par_name + self._ch_name
        return par_name + "/" + self._ch_name
