from sanic import response
from uniswap import Uniswap
from webargs import fields

from app import get_app, jinja
from project.models import Token, CHAINS, Wallet
from utils.crud import get_list
from utils.wei_converter import to_basis_points, from_basis_points
from validation import use_kwargs

app = get_app()


@jinja.template("swap.html")
async def swap_view(request, chain_id=None):
    if not chain_id:
        return response.redirect(app.url_for("admin.swap_in_chain", chain_id=137))
    return {
        "tokens": await get_list(Token),
        "chains": CHAINS,
        "chain_id": int(chain_id) if chain_id else None,
    }


@use_kwargs({
    "token_from_address": fields.Str(),
    "token_to_address": fields.Str(),
    "chain_id": fields.Int(),
    "dex": fields.Str(),
    "amount": fields.Str(),
}, location='form')
async def get_amount_token_to_token_swap_view(
        request,
        token_from_address,
        token_to_address,
        chain_id,
        dex,
        amount
    ):
    token_from = await Token.find_one({
        "address": token_from_address,
        "chain_id": chain_id
    })
    token_to = await Token.find_one({
        "address": token_to_address,
        "chain_id": chain_id
    })

    assert token_to and token_from, 'Token(s) not found'

    amount = to_basis_points(amount, token_from.decimals)

    chain = CHAINS[chain_id]
    w3 = chain.get_web3_instance()

    client = None
    if dex == 'uniswap_v2':
        client = Uniswap(
            version=2, web3=w3,
            # нам не нужен кошелек, чтобы просто посмотреть цену
            address=None, private_key=None,
            # uniswap-python не знает адреса в polygon, там это quickswap
            factory_contract_addr=chain.uniswap_v2_factory,
            router_contract_addr=chain.uniswap_v2_router,
        )
    if dex == 'uniswap_v3':
        # тут все проще чем с v2
        client = Uniswap(version=3, web3=w3, address=None, private_key=None)

    assert client is not None, 'DEX not found'

    price_basis_points = client.get_price_input(
        token_from.address, token_to.address, amount,
        # можно эксперементировать с route, но работает только в v2
        # route=[token_from_address, token_to_address]
    )

    return response.json({
        "amount": '%.6f' % from_basis_points(price_basis_points, token_from.decimals),
        "amount_basis_points": str(price_basis_points)
    })
