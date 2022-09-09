import aiohttp
from eth_utils import to_wei
from marshmallow import ValidationError
from web3.exceptions import ContractLogicError

from project.models import CHAINS, Token, DEXS
from project.tasks import cronjob, manage_task


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


@manage_task()
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
