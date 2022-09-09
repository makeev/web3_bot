from decimal import Decimal, localcontext

from sanic import response
from webargs import fields

from app import get_app, jinja
from sanic.views import HTTPMethodView

from project.models import Token, CHAINS, DEXS
from utils.crud import get_list
from utils.wei_converter import to_basis_points, from_basis_points
from utils.zerox import ZeroXProtocol
from validation import use_kwargs

app = get_app()


class ArbView(HTTPMethodView):
    @jinja.template("arb.html")
    async def get(self, request):
        return {
            # "tokens": await get_list(Token, {"$or": [{"is_base_asset": True}, {"is_tradable": True}]}),
            "tokens": await get_list(Token),
            "chain": CHAINS[137],  # пока нас интересует только polygon
        }


@use_kwargs({
    "path": fields.List(fields.Str()),
    "amount": fields.Str(),
}, location='form')
async def calc_arb_path_view(request, path, amount):
    chain = CHAINS[137]
    token_from = await Token.get_by_address_n_chain(path[0], chain.chain_id)
    amount_basis_points = to_basis_points(amount, token_from.decimals)

    change = []
    for i, address in enumerate(path):
        change.append(address)
        if len(change) == 3:  # пора менять
            token_from = await Token.get_by_address_n_chain(change[0], chain.chain_id)
            token_to = await Token.get_by_address_n_chain(change[2], chain.chain_id)
            dex = DEXS[chain.chain_id][change[1]]

            amount_basis_points = await dex.get_price_input(
                token_from, token_to, amount_basis_points
            )
            change = [token_to.address]

    return response.json({
        "amount_basis_points": str(amount_basis_points),
        "amount": from_basis_points(amount_basis_points, token_to.decimals)
    })


@use_kwargs({
    "path": fields.List(fields.Str()),
    "amount": fields.Str(),
}, location='form')
async def simulate_0x_trade_view(request, path, amount):
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

    return response.json({
        "amount_basis_points": str(amount_bpt),
        "amount": from_basis_points(amount_bpt, token_to.decimals)
    })
