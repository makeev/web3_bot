import random

from coloring import print_red, print_green, print_bdark_green, print_bdebian_red, print_orchid
from decimal import Decimal, localcontext

from project.models import Token, CHAINS, Wallet, Deal, DEXS
from project.tasks import manage_task
from utils.arb import calc_arb_by_path
from utils.crud import get_list
from utils.swap import zx_swap_token_to_token
from utils.wei_converter import to_basis_points, from_basis_points
from utils.zerox import ZeroXProtocol, ZeroXException


async def token_to_token_arb_trade(from_symbol, to_symbol, initial_amount):
    """
    Меняем стейблкоины у которых знаем конечную стоимость в фиате,
    пытаемся выиграть при обмене на фиат
    """
    chain = CHAINS[137]  # Polygon
    w3 = chain.get_web3_instance()

    with localcontext() as ctx:
        ctx.prec = 999

        # @TODO хардкодим кошелек
        wallet = await Wallet.find_one({"address": "0xe7b0226Cf0fe4F526B48Be6D6cAcdE897a3212b6"})
        assert wallet is not None

        token_from = await Token.find_one({"symbol": from_symbol, "chain_id": chain.chain_id})
        token_to = await Token.find_one({"symbol": to_symbol, "chain_id": chain.chain_id})
        initial_amount = Decimal(initial_amount)
        amount_bpt = to_basis_points(initial_amount, token_from.decimals)
        wallet_token_amount_bpt = await wallet.get_token_balance(from_symbol, chain.chain_id)

        # используем uniswap, чтобы посчитать затраты газа в usdc
        uniswap = DEXS[chain.chain_id]['uniswap_v2']
        USDC = await Token.get_by_symbol_n_chain("USDC", chain.chain_id)

        print_orchid('trade from %s to %s' % (from_symbol, to_symbol))
        print_orchid('wallet balance: %s %s' % (from_symbol, from_basis_points(wallet_token_amount_bpt, decimals=token_from.decimals)))
        print_orchid('trade amount: %s %s' % (from_symbol, from_basis_points(amount_bpt, decimals=token_from.decimals)))

        async with ZeroXProtocol() as zx:
            while True:
                assert wallet_token_amount_bpt > amount_bpt, 'Not enough %s tokens for trade' % from_symbol

                try:
                    r = await zx.quote(
                        sellToken=token_from.address,
                        buyToken=token_to.address,
                        sellAmount=amount_bpt,
                        # @TODO вынести куда-то настройку slippage
                        takerAddress=wallet.address,
                        slippagePercentage=0,  # мы не хотим slippage
                        intentOnFilling='true',
                        # @TODO валидация проверяет approve для ERC20 токена,
                        #  надо ловить эти ошибки и запускать approve до обмена
                        skipValidation='false'
                    )
                    # zx данные по смарт-контракту для обмена
                    data = await r.json()

                    # просто для информации собираем через что идет обмен
                    sources = []
                    for src in data['sources']:
                        if Decimal(src['proportion']) > 0:
                            sources.append(src['name'])

                    # считаем потенциальный профит
                    price = Decimal(from_basis_points(data['buyAmount'], token_to.decimals))
                    arb_diff = price - initial_amount

                    # и потенциальный tx fee
                    tx_fee = int(data['gas']) * int(data['gasPrice'])

                    # переводим в usd, чтобы посчитать профит
                    tx_fee_usd = from_basis_points(await uniswap.get_price_input('WMATIC', USDC, tx_fee),
                                                   decimals=USDC.decimals)

                    message = '%s: price %s, diff: %s, tx_fee: %s, sources: %s' % (data['decodedUniqueId'], price, arb_diff, tx_fee_usd, ",".join(sources))

                    do_trade = arb_diff > tx_fee_usd  # условный профит больше условной комиссии

                    if do_trade:
                        # разрешаем контракту тратить наши токены
                        await wallet.approve_if_needed(token_from, data['allowanceTarget'], chain.chain_id)

                        # подписываем и шлем транзакцию
                        tx_hash = await zx_swap_token_to_token(wallet, data)

                        # ждем receipt
                        print('https://polygonscan.com/tx/%s' % tx_hash.hex())
                        receipt = await w3.eth.wait_for_transaction_receipt(tx_hash)

                        if receipt['status'] == 1:
                            # записываем сделку в базу
                            # @TODO добавить информацию о sources в модель Deal
                            await Deal.get_or_create_from_transaction(
                                Deal.Types.USD_ARB.value,
                                tx_hash.hex(),
                                chain.chain_id,
                                save=True
                            )
                            print_green(message)
                        else:
                            print_red(message)

                        wallet_token_amount_bpt = await wallet.get_token_balance(from_symbol, chain.chain_id)

                except ZeroXException as e:
                    pass


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
async def dai_usdc_10_arb(app):
    await token_to_token_arb_trade("DAI", "USDC", 10)


@manage_task()
async def dai_usdc_100_arb(app):
    await token_to_token_arb_trade("DAI", "USDC", 100)


@manage_task()
async def usdt_dai_100_arb(app):
    await token_to_token_arb_trade("USDT", "DAI", 100)
