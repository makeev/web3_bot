from asyncio import get_event_loop
from datetime import datetime, timezone
from enum import Enum

from sanic.response import HTTPResponse
from sanic.server import HttpProtocol
from umongo import fields


def raw_json(
        body,
        status=200,
        headers=None,
        content_type="application/json",
):
    return HTTPResponse(
        body,
        headers=headers,
        status=status,
        content_type=content_type,
    )


def add_timestamp(doc_class):
    """
    Decorator to add `created_at` and `updated_at` to
    a document class. And use pre_insert and pre_update to
    update them
    """
    doc_class.created_at = fields.DateTimeField(required=False)
    doc_class.updated_at = fields.DateTimeField(required=False)

    def __add_create_timestamp(doc):
        doc.created_at = datetime.now(timezone.utc)

    def __add_update_timestamp(doc):
        doc.updated_at = datetime.now(timezone.utc)

    doc_class.pre_insert = __add_create_timestamp
    doc_class.pre_update = __add_update_timestamp
    return doc_class


async def init_sanic_app(app,
                         debug=False,
                         backlog=100,
                         access_log=None,
                         ):
    """
    Init sanic app, db, redis poll, etc.
    """
    # if access_log is passed explicitly change config.ACCESS_LOG
    if access_log is not None:
        app.config.ACCESS_LOG = access_log

    # initiate config and events listeners
    server_settings = app._helper(
        host=None,
        port=None,
        debug=debug,
        ssl=None,
        sock=None,
        unix=None,
        loop=get_event_loop(),
        protocol=HttpProtocol,
        backlog=backlog,
        run_async=False,
    )

    # fake server running
    app.is_running = True
    app.is_stopping = False

    # initiate start events (init mongo, redis, etc)
    await app._startup()
    await app._server_event("init", "before", loop=get_event_loop())


async def init_default_app_helper():
    """
    Call from python console to get app ready
    """
    from app import get_app
    app = get_app()
    await init_sanic_app(app)

    return app


class MyEnum(Enum):
    @classmethod
    def choices(cls) -> list:
        return [v.value for v in cls.__members__.values()]

    @classmethod
    def keys(cls) -> list:
        return [v.name for v in cls.__members__.values()]


def get_real_ip(request):
    addresses = request.remote_addr.split(',')
    return addresses[0].strip()
