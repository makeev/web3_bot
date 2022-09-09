from functools import wraps, partial

import pycron

from app import get_app

app = get_app()
app.ctx.cron_tasks = []


class ManageTask:
    """
    Обертка для тасков
    """
    def __init__(self, to_call, cron_string=None):
        self.to_call = to_call
        self.cron_string = cron_string

    def is_time(self):
        if self.cron_string:
            return pycron.is_now(self.cron_string)

    def run(self):
        return self.to_call()

    def __str__(self):
        return '%s' % self.to_call


def cronjob(cron_string):
    def decorator(function):
        @wraps(function)
        def wrapper(app):
            to_call = partial(function, app)
            return ManageTask(to_call, cron_string)
        # add task to register
        app.ctx.cron_tasks.append(wrapper)
        return wrapper

    return decorator


def manage_task():
    def decorator(function):
        @wraps(function)
        def wrapper(app):
            to_call = partial(function, app)
            return ManageTask(to_call)
        return wrapper

    return decorator


