import asyncio

import aiohttp
import pycron
from functools import wraps, partial
from app import get_app
from project.models import Token, CHAINS
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
        return self.to_call()

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


@cronjob("0 * * * *")
async def parse_uniswap_tokens(app):
    async def _get_or_create_token(row, address, chain_id):
        chain = CHAINS.get(int(chain_id))
        if not chain:
            return 0

        token = await Token.find_one({
            "symbol": row['symbol'],
            "chain_id": chain.chain_id,
        })
        if token:
            return 0

        token = Token(symbol=row['symbol'])

        try:
            token.address = address
            token.name = row['name']
            token.decimals = row['decimals']
            token.logo_uri = row['logoURI']
            token.is_active = True
            token.chain_id = chain.chain_id
            await token.commit()
        except ValidationError as e:
            print(e, row)
            return 0
        else:
            return 1

    async with aiohttp.ClientSession() as session:
        r = await session.get('https://tokens.uniswap.org/')
        assert r.status == 200

        data = await r.json()
        counter = 0
        for row in data['tokens']:
            counter += await _get_or_create_token(row, row['address'], row['chainId'])
            # смотрим есть ли этот токен в других сетях
            bridge_info = row.get('extensions', {}).get('bridgeInfo', {})
            for chain_id, data in bridge_info.items():
                counter += await _get_or_create_token(row, data['tokenAddress'], chain_id)

        print('%d tokens added' % counter)



