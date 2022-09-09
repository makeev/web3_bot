import random

from coloring import print_red, print_green, print_bdark_green, print_bdebian_red
from decimal import Decimal, localcontext

from project.models import Token, CHAINS
from project.tasks import manage_task
from utils.arb import calc_arb_by_path
from utils.crud import get_list
from utils.wei_converter import to_basis_points, from_basis_points
from utils.zerox import ZeroXProtocol, ZeroXException


async def token_to_token_arb_trade(from_symbol, to_symbol, initial_amount):
    chain = CHAINS[137]

    with localcontext() as ctx:
        ctx.prec = 999

        token_from = await Token.find_one({"symbol": from_symbol, "chain_id": chain.chain_id})
        token_to = await Token.find_one({"symbol": to_symbol, "chain_id": chain.chain_id})
        initial_amount = Decimal(initial_amount)
        amount_bpt = to_basis_points(initial_amount, token_from.decimals)

        async with ZeroXProtocol() as zx:
            while True:
                try:
                    r = await zx.quote(
                        sellToken=token_from.address,
                        buyToken=token_to.address,
                        sellAmount=amount_bpt,
                        slippagePercentage=0.005,
                    )
                    data = await r.json()
                    sources = []
                    for src in data['sources']:
                        if Decimal(src['proportion']) > 0:
                            sources.append(src['name'])

                    price = Decimal(from_basis_points(data['buyAmount'], token_to.decimals))
                    arb_diff = price - initial_amount
                    message = '%s: price %s, diff: %s, sources: %s' % (data['decodedUniqueId'], price, arb_diff, ",".join(sources))
                    if arb_diff > 0:
                        if arb_diff > 0.02:
                            print_func = print_green
                        else:
                            print_func = None
                    else:
                        print_func = None

                    if print_func:
                        print_func(message)
                except ZeroXException as e:
                    print_bdebian_red(e)


async def random_dai_triangular_arb(base_symbol, initial_amount):
    chain = CHAINS[137]

    with localcontext() as ctx:
        ctx.prec = 999

        base_token = await Token.find_one({"symbol": base_symbol, "chain_id": chain.chain_id})
        tradable_tokens = await get_list(Token, {
            "chain_id": chain.chain_id,
            "is_tradable": True,
            "symbol": {"$nin": [base_token.symbol]}
        })
        initial_amount = Decimal(initial_amount)

        while True:
            # LINK, PLA, SAND, MANA, WMATIC, BAL, ERN, RBC, WBTC, SUSHI, SHIB
            intermidiate_tokens = random.choices(tradable_tokens, k=random.randint(1,2))
            path = [base_token] + intermidiate_tokens + [base_token]
            path_addresses = [t.address for t in path]

            try:
                result_amount = await calc_arb_by_path(path_addresses, initial_amount)
                message = '%s ' % initial_amount + '-'.join([t.symbol for t in path]) + ' = %s' % result_amount

                if result_amount > initial_amount:
                    print_green(message)
            except ZeroXException as e:
                print([t.symbol for t in path])
                print_red(e)


async def path_triangular_arb(path_symbols, initial_amount):
    chain = CHAINS[137]

    with localcontext() as ctx:
        ctx.prec = 999
        initial_amount = Decimal(initial_amount)
        path_tokens = [await Token.find_one({"chain_id": chain.chain_id, "symbol": symbol}) for symbol in path_symbols]
        path_addresses = [t.address for t in path_tokens]

        while True:
            try:
                result_amount = await calc_arb_by_path(path_addresses, initial_amount)
                message = '%s ' % initial_amount + '-'.join([t.symbol for t in path_tokens]) + ' = %s' % result_amount

                if result_amount > initial_amount:
                    print_green(message)
                else:
                    # print(message)
                    pass
            except ZeroXException as e:
                print([t.symbol for t in path_tokens])
                print_red(e)


@manage_task()
async def weth_dai_weth_arb_100(app):
    await path_triangular_arb(['WETH', 'DAI', 'WETH'], 0.1)


@manage_task()
async def usdc_dai_usd_arb_100(app):
    await path_triangular_arb(['USDC', 'DAI', 'USDC'], 100)

@manage_task()
async def usdc_sand_usd_arb_100(app):
    await path_triangular_arb(['USDC', 'SAND', 'USDC'], 100)


@manage_task()
async def trinagular_usdc_1000(app):
    await random_dai_triangular_arb('USDC', 1000)


@manage_task()
async def usdc_dai_10_arb(app):
    await token_to_token_arb_trade("USDC", "DAI", 10)


@manage_task()
async def usdc_dai_100_arb(app):
    await token_to_token_arb_trade("USDC", "DAI", 100)


@manage_task()
async def usdc_dai_1000_arb(app):
    await token_to_token_arb_trade("USDC", "DAI", 1000)


@manage_task()
async def dai_usdt_100_arb(app):
    await token_to_token_arb_trade("DAI", "USDT", 100)


@manage_task()
async def dai_usdc_100_arb(app):
    await token_to_token_arb_trade("DAI", "USDC", 100)


@manage_task()
async def usdt_dai_100_arb(app):
    await token_to_token_arb_trade("USDT", "DAI", 100)
