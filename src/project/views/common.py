from sanic import response

import settings
from app import get_app, jinja
from utils.auth import token_required
from project.tasks import sleepy_task

app = get_app()


@jinja.template("index.html")
async def index_view(request) -> response.HTTPResponse:
    return {}


@jinja.template("admin_index.html")
async def admin_home_view(request) -> response.HTTPResponse:
    return app.config


@token_required
async def test_view(request, param):
    # async task
    app.add_task(sleepy_task(app, custom_param=param))

    return response.html("<b>test url: <a href='{url}'>home</a></b>".format(
        url=app.url_for('home')
    ))


async def debug_view(request):
    vars_to_print = ['DEBUG', 'MONGO_DB']
    return response.json({k: getattr(settings, k) for k in vars_to_print})


