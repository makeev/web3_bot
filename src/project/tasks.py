import asyncio

import aiohttp
import pycron
from functools import wraps, partial

from eth_utils import to_wei
from web3.exceptions import ContractLogicError

from app import get_app
from project.models import Token, CHAINS, DEXS
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


@cronjob("0 * * * *")
async def check_tokens_liquidity(app):
    # @TODO слишком простой метод, не учитывает разные сети и биржи

    dex = DEXS[137]['uniswap_v2']
    client = dex.get_uniswap_instance()
    token_from = await Token.find_one({"chain_id": 137, "symbol": "WETH"})

    async for token in Token.find({"is_active": True}):
        print(token.symbol)
        try:
            amount_basis_points = client.get_price_input(
                token_from.address, token.address, to_wei('1.0', 'ether'),
            )
            token.is_tradable = amount_basis_points > 0
        except ContractLogicError:
            token.is_tradable = False
        finally:
            await token.commit()
