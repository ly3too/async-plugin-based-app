import asyncio as aio
import time

async def main():
    await aio.sleep(2)
    await aio.sleep(2)
    await aio.sleep(2)

if __name__ == "__main__":
    t = time.time()
    loop = aio.get_event_loop()
    loop.run_until_complete(main())
    diff = time.time() - t
    print(diff)