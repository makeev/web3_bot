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


app.blueprint(admin)
