from sanic import response
from sanic.views import HTTPMethodView
from web3 import Web3
from webargs import fields

from app import get_app, jinja
from project.models import Token, CHAINS
from utils.crud import get_pagination_context_for, get_object_or_404
from validation import use_kwargs

app = get_app()


@jinja.template("tokens.html")
async def list_tokens_view(request):
    return await get_pagination_context_for(Token, request, limit=1000, sort=[("symbol", 1)])


@use_kwargs({
    "field": fields.Str(),
}, location='form')
async def toggle_token_bool_field_view(request, id, field):
    token = await get_object_or_404(Token, id)
    setattr(token, field, not getattr(token, field))
    await token.commit()

    return response.json({
        field: getattr(token, field),
    })


class CreateTokenView(HTTPMethodView):
    @jinja.template("token_form.html")
    async def get(self, request):
        return {
            "chains": CHAINS,
        }

    @use_kwargs({
        "name": fields.Str(required=True),
        "address": fields.Str(required=True),
        "symbol": fields.Str(required=True),
        "chain_id": fields.Str(required=True),
        "decimals": fields.Int(required=True),
        "logo_uri": fields.Str(required=False),
    }, location="form")
    async def post(self, request, **kwargs):
        kwargs['address'] = Web3.toChecksumAddress(kwargs['address'])
        token = Token(**kwargs)
        await token.commit()

        return response.redirect(app.url_for("admin.token_list"))


async def get_abi_view(request, id):
    token = await get_object_or_404(Token, id)

    token.abi = await token.get_abi()
    await token.commit()

    return response.json({"success": bool(token.abi)})
