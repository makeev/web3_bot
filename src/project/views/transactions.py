from app import jinja, get_app

from project.models import Transaction, Contract, Token
from utils.crud import get_pagination_context_for

app = get_app()


async def get_known_addresses() -> dict:
    known_addresses = {}

    cursor = Contract.find({})
    async for contract in cursor:
        known_addresses[contract.address] = contract.name

    cursor = Token.find({})
    async for token in cursor:
        known_addresses[token.address] = token.name

    return known_addresses


@jinja.template("transactions.html")
async def transactions_list_view(request):
    print(request.query_args)
    condition = {}

    # смотрим какие фильтры применены
    filters = {}
    for query_key, value in request.query_args:
        if value and query_key.startswith('filters'):
            _, filter_field = query_key.split(':')
            filters[filter_field] = str(value)
            if value.startswith('>'):
                condition[filter_field] = {"$gte": float(value[1:])}
            else:
                condition[filter_field] = {"$regex": value, "$options": "i"}

    print(condition)
    # собираем знакомые адреса, чтобы красиво их показать
    known_addresses = await get_known_addresses()

    context = await get_pagination_context_for(Transaction, request, 100, condition=condition)
    context['known_addresses'] = known_addresses
    context['filters'] = filters
    return context
