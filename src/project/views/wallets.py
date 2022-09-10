from eth_utils.currency import from_wei
from sanic import response
from sanic.exceptions import InvalidUsage
from sanic.views import HTTPMethodView
from webargs import fields

from app import get_app, jinja
from project.models import Wallet, CHAINS, Token
from utils.crud import get_pagination_context_for, delete_by_id, get_object_or_404
from validation import use_kwargs

app = get_app()


@jinja.template("wallets.html")
async def list_wallets_view(request):
    return await get_pagination_context_for(Wallet, request, limit=100)


class WalletCreateView(HTTPMethodView):
    @jinja.template("wallet_form.html")
    async def get(self, request):
        return {}

    @use_kwargs({
        "name": fields.Str(required=True),
        "address": fields.Str(required=True),
        "private_key": fields.Str(required=True),
    }, location='form')
    async def post(self, request, name, address, private_key):
        is_wallet_exists = await Wallet.find_one({"address": address})
        if is_wallet_exists:
            raise InvalidUsage("contract already exists")

        wallet = Wallet(name=name, address=address, private_key=private_key)
        await wallet.commit()

        return response.redirect(app.url_for("admin.wallets_list"), status=301)


async def delete_wallet_view(request, id):
    r = await delete_by_id(Wallet, id)
    return response.json({"success": r.deleted_count > 0, "deleted_count": r.deleted_count})


async def get_native_balances_view(request, id):
    wallet = await get_object_or_404(Wallet, id)

    balances = {}
    for chain_id, chain in CHAINS.items():
        balances[chain.name] = {
            "amount": from_wei(await wallet.get_token_balance(chain.currency_symbol, chain.chain_id), 'ether'),
            "symbol": chain.currency_symbol
        }

    return response.json(balances)


@use_kwargs({
    "token": fields.Str(),
    "chain_id": fields.Int(),
})
async def add_token_view(request, id, token, chain_id):
    wallet = await get_object_or_404(Wallet, id)
    chain = CHAINS[chain_id]

    if token.startswith('0x'):
        # ищем токен по адресу
        # token = await Token.
        pass
