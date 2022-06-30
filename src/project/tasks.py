import asyncio


async def sleepy_task(app, custom_param):
    """
    For test
    """
    print(custom_param)
    await asyncio.sleep(5)
