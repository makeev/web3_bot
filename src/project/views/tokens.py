from sanic import response
from webargs import fields

from app import get_app, jinja
from project.models import Token
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
