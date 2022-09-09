from decimal import localcontext, Decimal

from project.models import CHAINS, Token
from utils.wei_converter import to_basis_points, from_basis_points
from utils.zerox import ZeroXProtocol


async def calc_arb_by_path(path, amount):
    chain = CHAINS[137]
    token_from = await Token.get_by_address_n_chain(path[0], chain.chain_id)
    amount_bpt = to_basis_points(amount, token_from.decimals)

    async with ZeroXProtocol() as zx:
        change = []
        for address in path:
            change.append(address)

            if len(change) == 2:
                # получаем данные по токенам
                token_from = await Token.get_by_address_n_chain(change[0], chain.chain_id)
                token_to = await Token.get_by_address_n_chain(change[1], chain.chain_id)

                # получаем данные от api 0z protocol
                r = await zx.quote(
                    sellToken=token_from.address,
                    buyToken=token_to.address,
                    sellAmount=amount_bpt,
                    slippagePercentage=0.005,  # полпроцента, максимум что мы можем себе позволить
                )
                data = await r.json()

                with localcontext() as ctx:
                    ctx.prec = 999
                    # amount_bpt = int(Decimal(data['guaranteedPrice']) * Decimal(data['sellAmount']))
                    amount_bpt = int(Decimal(data['guaranteedPrice']) * Decimal(to_basis_points(amount, token_to.decimals)))
                    amount = from_basis_points(amount_bpt, token_to.decimals)
                change = [token_to.address]

    return from_basis_points(amount_bpt, token_to.decimals)
