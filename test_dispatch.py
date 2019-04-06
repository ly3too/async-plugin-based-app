import asyncio as aio
from asyncio.events import AbstractEventLoop
from adispatch.dispatch import Dispatcher
from adispatch.channel import Channel

async def print_message(loop: AbstractEventLoop, signal, message, sender, *args, **kwargs):
    print ("printer received: {}, {}, {}".format(signal, message, sender))
    await aio.sleep(4)

async def print_tasks(loop):
    print("t1")
    while True:
        await aio.sleep(3)
        print("all tasks:{}".format(len(aio.Task.all_tasks(loop=loop))))

async def pub_mess(ch: Dispatcher):
    print("t2")
    while True:
        await aio.sleep(2)
        print ("publish a message")
        await ch.pub("example", {"name": "test"}, "me")

async def lev1_handle(loop: AbstractEventLoop, signal, message, sender, *args, **kwargs):
    print ("lev1 received: {}, {}, {}".format(signal, message, sender))
    await aio.sleep(4)

async def lev2_handle(loop: AbstractEventLoop, signal, message, sender, *args, **kwargs):
    print ("lev2 received: {}, {}, {}".format(signal, message, sender))
    await aio.sleep(4)

async def root_handle(loop: AbstractEventLoop, signal, message, sender, *args, **kwargs):
    print ("root received: {}, {}, {}".format(signal, message, sender))
    await aio.sleep(4)

async def pub_tree(loop:AbstractEventLoop, root:Channel):
    while True:
        await aio.sleep(2)
        print ("pub root")
        await root.pub("signal", "message from root channel")
        await aio.sleep(2)
        print ("pub lev1")
        await root.get_or_create_sub_ch("/lev1").pub("signal", "message from channel lev1")
        await aio.sleep(2)
        print ("pub lev2")
        await root.get_or_create_sub_ch("/lev1/lev2").pub("signal", "message from channel lev2")


async def main(loop):
    ch = Dispatcher(loop)
    await ch.sub("example", print_message)
    t1 = aio.ensure_future(print_tasks(loop))
    t2 = aio.ensure_future(pub_mess(ch))

    root = Channel(loop)
    print("root: {}".format(root.get_ch_name()))
    lev2 = root.get_or_create_sub_ch("/lev1/lev2")
    print("lev2: {}".format(lev2.get_ch_name()))
    lev1 = root.get_sub_ch("/lev1")
    print("lev1: {}".format(lev1.get_ch_name()))
    await lev1.sub("signal", lev1_handle)
    await lev2.sub("signal", lev2_handle)
    await root.sub("signal", root_handle)
    t3 = aio.ensure_future(pub_tree(loop, root))
    await aio.gather(t1, t2, t3)

if __name__ == "__main__":
    loop = aio.get_event_loop()
    loop.run_until_complete(main(loop))
    aio.sleep(2)
    loop.close()
