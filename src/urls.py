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
admin.add_route(views.toggle_token_bool_field_view, "/tokens/<id>/toggle_bool_field", methods=["POST"], name="toggle_token_bool_field")
admin.add_route(views.CreateTokenView.as_view(), "/tokens/add", methods=["GET", "POST"], name="token_add")
admin.add_route(views.get_abi_view, "/tokens/<id>/get_abi", methods=["POST"], name="token_get_abi")
admin.add_route(views.delete_token_view, "/tokens/<id>", methods=["DELETE"], name="token_delete")

# indexes
admin.add_route(views.indexes_view, "/indexes", methods=["GET"], name="indexes")
admin.add_route(views.delete_index_view, "/indexes/<model_name>/<index_name>", methods=["DELETE"])
admin.add_route(views.create_index_view, "/indexes/<model_name>", methods=["POST"])
admin.add_route(views.ensure_indexes_view, "/indexes/ensure/<model_name>", methods=["POST"])

# swap
admin.add_route(views.swap_view, "/swap", methods=["GET"], name="swap")
admin.add_route(views.swap_view, "/swap/<chain_id>", methods=["GET"], name="swap_in_chain")
admin.add_route(views.get_amount_token_to_token_swap_view, "/swap/get_amount", methods=["POST"], name="swap_get_amount")

# wallets
admin.add_route(views.list_wallets_view, "/wallets", methods=["GET"], name="wallets_list")
admin.add_route(views.WalletCreateView.as_view(), "/wallets/add", methods=["GET", "POST"], name="wallets_add")
admin.add_route(views.delete_wallet_view, "/wallets/<id>", methods=["DELETE"], name="wallets_delete")
admin.add_route(views.get_balances_view, "/wallets/<id>/balances", methods=["GET"], name="wallets_balances")
admin.add_route(views.import_token_view, "/wallets/<id>/import_token", methods=["POST"], name="wallet_import_token")

# arb
admin.add_route(views.ArbView.as_view(), "/arb", methods=["GET"], name="arb")
admin.add_route(views.calc_arb_path_view, "/arb/calc", methods=["POST"], name="arb_calc")
admin.add_route(views.simulate_0x_trade_view, "/arb/zx_simulate", methods=["POST"], name="arb_zx_simulate")

# deals
admin.add_route(views.deals_list_view, "/deals", methods=["GET"], name="deal_list")

app.blueprint(admin)
