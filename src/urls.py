from app import get_app
from project import views
from sanic import Blueprint


app = get_app()
app.add_route(views.index_view, "/")

admin = Blueprint("admin", url_prefix="/admin")
admin.add_route(views.admin_home_view, "/", name="home")

# users
admin.add_route(views.list_users_view, "/users", methods=["GET"], name="user_list")
admin.add_route(views.UserUpdateView.as_view(), "/users/<id>", methods=["GET", "POST"], name="user_details")
admin.add_route(views.UserCreateView.as_view(), "/users/add", methods=["GET", "POST"], name="user_add")
admin.add_route(views.delete_user_api_view, "/users/<id>", methods=["DELETE"], name="user_delete")
admin.add_route(views.login_view, "/login", methods=["GET", "POST"], name="user_login")

# test and debug
admin.add_route(views.test_view, "/test/<param>", name="test", methods=["GET"])
admin.add_route(views.debug_view, '/debug', methods=['GET'])
admin.add_route(views.staff_view, "/staff", methods=["GET", "POST"])

# transactions
admin.add_route(views.transactions_list_view, "/transactions", methods=["GET"], name="transactions_list")

# contracts
admin.add_route(views.contracts_list_view, "/contracts", methods=["GET"], name="contracts_list")
admin.add_route(views.ContractCreateView.as_view(), "/contracts/add", methods=["GET", "POST"], name="contracts_add")
admin.add_route(views.delete_contract_view, "/contracts/<id>", methods=["DELETE"], name="contracts_delete")

# tokens
admin.add_route(views.list_tokens_view, "/tokens", methods=["GET"], name="token_list")

# indexes
admin.add_route(views.indexes_view, "/indexes", methods=["GET"], name="indexes")
admin.add_route(views.delete_index_view, "/indexes/<model_name>/<index_name>", methods=["DELETE"])
admin.add_route(views.create_index_view, "/indexes/<model_name>", methods=["POST"])
admin.add_route(views.ensure_indexes_view, "/indexes/ensure/<model_name>", methods=["POST"])

# swap
admin.add_route(views.swap_view, "/swap", methods=["GET"], name="swap")
admin.add_route(views.swap_view, "/swap/<chain_id>", methods=["GET"], name="swap_in_chain")

app.blueprint(admin)
