from app import get_app, jinja
from project.models import Token
from utils.crud import get_pagination_context_for

app = get_app()


@jinja.template("tokens.html")
async def list_tokens_view(request):
    return await get_pagination_context_for(Token, request, limit=100)
