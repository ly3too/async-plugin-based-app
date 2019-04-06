from pluginbase import PluginBase
import asyncio as aio
from adispatch.channel import Channel
import logging
from asyncio.events import AbstractEventLoop

class MainLoop:
    def __init__(self, loop: AbstractEventLoop):
        # init event loop and dispatcher
        self._loop = loop
        self._ch = Channel(self._loop)
        logging.basicConfig(format='%(asctime)s [%(levelname)s] (%(pathname)s:%(lineno)d): %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        self._loger = logging.getLogger()
        self._loger.setLevel("DEBUG")

        # load plugins
        plugin_base = PluginBase("my_plugin")
        self._plugin_source = plugin_base.make_plugin_source(searchpath=["./plugins"])
        self._plugins = dict()
        for name in self._plugin_source.list_plugins():
            self._loger.debug("loading: " + name)
            plugin = self._plugin_source.load_plugin(name)
            if hasattr(plugin, "setup"):
                self._plugins[name] = plugin.setup(self._loop, self._ch, self._loger)

        # after setup
        self._loop.run_until_complete(self.on_setup_done())

    async def on_setup_done(self):
        for _, app in self._plugins.items():
            self._loop.create_task(app.on_setup_done())

    async def exit(self):
        self._loop.close()

    # run all plugins
    def run(self):
        self._loger.debug("plugins: {}".format(self._plugins))
        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            for task in aio.Task.all_tasks(loop=self._loop):
                task.cancel()
            self._loop.create_task(self.exit())

    def __del__(self):
        for plugin in self._plugins:
            if hasattr(plugin, "destroy"):
                plugin.destroy()

if __name__ == "__main__":
    loop = aio.get_event_loop()
    loop.set_debug(True)
    app = MainLoop(loop)
    app.run()

