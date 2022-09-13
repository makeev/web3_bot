from math import ceil

from app import jinja, get_app

from project.models import Transaction, Contract, Token, CHAINS, Deal
from utils.crud import get_pagination_context_for

app = get_app()


@jinja.template("deals.html")
async def deals_list_view(request):
    """
    Return pagination context for defined model
    """
    page = int(request.args.get('page', 1))
    total = await Deal.count_documents()
    limit = 100
    pages = range(1, ceil(total / limit) + 1)
    sort =[("$natural", -1)]

    cursor = Deal.find({}).limit(limit).skip((page - 1) * limit).sort(sort)
    objects = []

    async for row in cursor:
        await row.sell_token.fetch()
        await row.buy_token.fetch()
        objects.append(row)

    return {
        "objects": objects,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages
    }
