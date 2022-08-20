from app import jinja

from project.models import Transaction
from utils.crud import get_pagination_context_for


@jinja.template("transactions.html")
async def transactions_list_view(request):
    return await get_pagination_context_for(Transaction, request, 1000)
