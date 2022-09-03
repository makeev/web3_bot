from sanic import response
from sanic.exceptions import InvalidUsage
from sanic.views import HTTPMethodView
from webargs import fields

from app import jinja, get_app
from project.models import Contract, CHAINS
from utils.crud import get_pagination_context_for, get_object_or_404, update_by_id, delete_by_id
from validation import use_kwargs


app = get_app()


@jinja.template("contracts.html")
async def contracts_list_view(request):
    return await get_pagination_context_for(Contract, request, 1000)


class ContractCreateView(HTTPMethodView):
    @jinja.template("contract_form.html")
    async def get(self, request):
        return {
            "chains": CHAINS
        }

    @use_kwargs({
        "name": fields.Str(required=True),
        "address": fields.Str(required=True),
        "abi": fields.Str(required=False, allow_none=True),
        "chain_id": fields.Int(required=True),
    }, location='form')
    async def post(self, request, name, address, chain_id, abi=None):
        is_contract_exists = await Contract.find_one({"address": address})
        if is_contract_exists:
            raise InvalidUsage("contract already exists")

        contract = Contract(name=name, address=address, abi=abi, chain_id=chain_id)
        if not contract.abi:
            contract.abi = await contract.get_abi()
        await contract.commit()

        return response.redirect(app.url_for("admin.contracts_list"), status=301)


async def delete_contract_view(request, id):
    r = await delete_by_id(Contract, id)
    return response.json({"success": r.deleted_count > 0, "deleted_count": r.deleted_count})
