import os
import time

import aioredis
from sanic.application.state import Mode
from sanic_jinja2 import SanicJinja2
from web3 import Web3, HTTPProvider

import settings
from sanic import Sanic
from sanic.log import logger, access_logger

from sanic_openapi import swagger_blueprint
from sanic_session import Session, AIORedisSessionInterface

from utils.mongo import register_mongo

import logging
if not settings.DEBUG:
    # disable the asyncio "Executing took ... seconds" warning
    logging.getLogger('asyncio').setLevel(logging.ERROR)

if settings.USE_TZ:
    os.environ['TZ'] = settings.TIMEZONE
    time.tzset()

APP_NAME = "project"
app = Sanic(APP_NAME, strict_slashes=True)
# to enable debug mode without --dev param
if settings.DEBUG:
    app.state.mode = Mode.DEBUG

app.blueprint(swagger_blueprint)


app.ctx.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
app.ctx.w3 = Web3(HTTPProvider(settings.ETH_HTTP_NODE_URL))
session = Session(app, interface=AIORedisSessionInterface(app.ctx.redis))
jinja = SanicJinja2(app, session=session)


def get_app():
    return Sanic.get_app(APP_NAME)


# set logging levels
logging.getLogger('sanic.root').setLevel(logging.INFO)

# update sanic config from settings
app.config.update({k: getattr(settings, k) for k in vars(settings) if k.isupper()})

# configure static files
app.static(settings.STATIC_URL, settings.STATIC_PATH)

register_mongo(
    app,
    mongo_uri=settings.MONGO_URI,
    mongo_db=settings.MONGO_DB,
    options={
        "minPoolSize": 10,
        "maxPoolSize": 50,
    }
)

# load middlewares
import middlewares

# load routing
import urls

logger.info('app initialized')
