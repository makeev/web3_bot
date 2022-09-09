#!/usr/bin/env python
import asyncio
import click
from coloring import print_orange
from app import get_app
from utils.common import init_sanic_app


async def main(task_name):
    app = get_app()
    await init_sanic_app(app)
    # импортируем заранее все что можно запускать
    from project import tasks

    print_orange('run! %s' % task_name)
    task = getattr(tasks, task_name)(app)
    await task.run()


if __name__ == '__main__':
    @click.command()
    @click.argument('task_name')
    def run(task_name):
        asyncio.run(main(task_name))

    run()
