from sanic import response
from app import get_app, jinja
from project.models import Token, CHAINS
from utils.crud import get_list

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
