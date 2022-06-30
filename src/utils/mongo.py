from motor.motor_asyncio import AsyncIOMotorClient
from sanic import Sanic
from sanic.log import logger
from umongo.frameworks import MotorAsyncIOInstance


def register_mongo(app: Sanic, mongo_uri, mongo_db, options: dict):
    # lazy init
    app.ctx.umongo = MotorAsyncIOInstance()

    @app.listener('before_server_start')
    def init_mongo(app, loop):
        if mongo_db and mongo_uri:
            motor_client = AsyncIOMotorClient(mongo_uri, **options)
            app.ctx.motor_client = motor_client
            app.ctx.motor_db = motor_client[mongo_db]
            app.ctx.umongo.set_db(motor_client[mongo_db])
            logger.info('mongo client created %s' % app.ctx.umongo)
        else:
            logger.error('mongo client not created: %s %s' % (mongo_uri, mongo_db))

    @app.listener('after_server_stop')
    async def mongodb_free_resources(app_inner, _loop):
        if hasattr(app.ctx, 'umongo_client'):
            app.ctx.motor_client.close()
            logger.info('mongo client closed')