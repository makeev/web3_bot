import asyncio
import time
from uuid import uuid4

from bson import ObjectId
from sanic.log import logger

from app import get_app
from project.models import Task
from project.models.task import TaskStatuses
from utils.common import init_sanic_app
from utils.sending import QueueManager

worker_id = uuid4().hex[:5]
logger.info('worker %s started' % worker_id)


async def main():
    await init_sanic_app(get_app())

    while True:
        # @TODO pycron
        try:
            await Task.run(task)
        except Exception:  # asyncio.CancelledError
            # @TODO catch timeout error
            logger.exception('exception during running task %s' % task_id)
            await Task.mark_as_error(task_id)
        finally:
            await Task.mark_as_finished(task_id)
            logger.info('task %s %s  finished in %.2f' % (task['type'], task_id, time.time() - start))

        # ждем новые таски
        await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
