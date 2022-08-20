from sanic import response
from sanic.exceptions import InvalidUsage
from sanic.views import HTTPMethodView
from webargs import fields

from app import jinja, get_app
from project.models import Contract
from utils.crud import get_pagination_context_for, get_object_or_404, update_by_id
from validation import use_kwargs


app = get_app()


@jinja.template("contracts.html")
async def contracts_list_view(request):
    return await get_pagination_context_for(Contract, request, 1000)


class ContractCreateView(HTTPMethodView):
    @jinja.template("contract_form.html")
    async def get(self, request):
        return {}

    @use_kwargs({
        "name": fields.Str(required=True),
        "address": fields.Str(required=True),
        "abi": fields.Str(required=True),
    }, location='form')
    async def post(self, request, name, address, abi):
        is_contract_exists = await Contract.find_one({"address": address})
        if is_contract_exists:
            raise InvalidUsage("contract already exists")

        contract = Contract(name=name, address=address, abi=abi)
        await contract.commit()

        return response.redirect(app.url_for("admin.contracts_list"), status=301)


class ContractUpdateView(HTTPMethodView):
    @jinja.template("contract_form.html")
    async def get(self, request, id):
        return {
            "obj": await get_object_or_404(Contract, id)
        }

    @use_kwargs({
        "name": fields.Str(required=True),
        "address": fields.Str(required=True),
        "abi": fields.Str(required=True),
    }, location='form')
    async def post(self, request, id, **kwargs):
        await update_by_id(Contract, id, **kwargs)
        return response.redirect(app.url_for('admin.contracts_list'), status=301)
