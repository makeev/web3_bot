import asyncio

import aiohttp
import pycron
from functools import wraps, partial
from app import get_app
from project.models import Token
from marshmallow.exceptions import ValidationError

app = get_app()
app.ctx.cron_tasks = []


class CronTask:
    def __init__(self, to_call, cron_string):
        self.to_call = to_call
        self.cron_string = cron_string

    def is_time(self):
        return pycron.is_now(self.cron_string)

    def run(self):
        return asyncio.create_task(self.to_call())

    def __str__(self):
        return '%s' % self.to_call


def cronjob(cron_string):
    def decorator(function):
        @wraps(function)
        def wrapper(app):
            to_call = partial(function, app)
            return CronTask(to_call, cron_string)
        # add task to register
        app.ctx.cron_tasks.append(wrapper)
        return wrapper

    return decorator


@cronjob("* */1 * * *")
async def parse_uniswap_tokens(app):
    redis = app.ctx.redis
    version_key = 'UNISWAP_TOKENS_LAST_PARSED_VERSION'
    last_parsed_version = await redis.get(version_key)

    print('last_parsed_version: %s' % last_parsed_version)
    async with aiohttp.ClientSession() as session:
        r = await session.get('https://tokens.uniswap.org/')
        assert r.status == 200

        data = await r.json()
        version = '%d_%d_%d' % (data['version']['major'], data['version']['minor'], data['version']['patch'])

        if last_parsed_version == version:
            return

        print('%s != %s' % (last_parsed_version, version))
        counter = 0
        for row in data['tokens']:
            if row['chainId'] != 1:
                # нужны только токены mainnet(chaindId=1)
                continue

            token = await Token.find_one({"symbol": row['symbol']})
            if not token:
                token = Token(symbol=row['symbol'])

            try:
                token.address = row['address']
                token.name = row['name']
                token.decimals = row['decimals']
                token.logo_uri = row['logoURI']
                token.extensions = row.get('extensions', {})
                token.is_active = True
                await token.commit()
            except ValidationError as e:
                print(e, row)
            else:
                counter += 1

        print('%d tokens parsed' % counter)
        await redis.set(version_key, version)



