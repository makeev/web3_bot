import asyncio
from app import get_app
from utils.common import init_sanic_app


async def main():
    app = get_app()
    await init_sanic_app(app)
    import project.tasks  # импортируем заранее все что можно запускать

    while True:
        for func in app.ctx.cron_tasks:
            task = func(app)
            is_now = task.is_time()
            if is_now:
                # @TODO тут еще можно как-то ловить статус выполнения таска потом
                asyncio.create_task(task.to_call())
                print('%s was run at %s' % (task, task.cron_string))
        await asyncio.sleep(60)


if __name__ == '__main__':
    asyncio.run(main())
