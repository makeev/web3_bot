from sanic import response
from sanic.exceptions import InvalidUsage
from sanic.views import HTTPMethodView
from webargs import fields

from app import get_app, jinja
from project.models import User
from utils.crud import get_pagination_context_for, get_object_or_404, update_by_id, delete_by_id
from validation import use_kwargs

app = get_app()


@jinja.template("users.html")
async def list_users_view(request):
    return await get_pagination_context_for(User, request, limit=100)


class UserCreateView(HTTPMethodView):
    @jinja.template("users_form.html")
    async def get(self, request):
        return {}

    @use_kwargs({
        "email": fields.Email(required=True),
        "name": fields.Str(required=True),
        "password": fields.Str(required=True)
    }, location='form')
    async def post(self, request, email, password, **kwargs):
        is_user_exists = await User.find_one({"email": email})
        if is_user_exists:
            InvalidUsage("email already registered")

        user = await User.create_user(email, password)
        user.update(kwargs)
        await user.commit()

        return response.redirect('/users', status=301)


class UserUpdateView(HTTPMethodView):
    @jinja.template("users_form.html")
    async def get(self, request, id):
        return {
            "obj": await get_object_or_404(User, id)
        }

    @use_kwargs({
        "name": fields.Str(required=True),
    }, location='form')
    async def post(self, request, id, **kwargs):
        await update_by_id(User, id, **kwargs)
        return response.redirect(app.url_for('admin.user_list'), status=301)


async def delete_user_api_view(request, id):
    r = await delete_by_id(User, id)
    return response.json({"success": r.deleted_count > 0, "deleted_count": r.deleted_count})


@jinja.template("login.html")
async def login_view(request):
    errors = []

    if request.method == "POST":
        cnt_users = await User.count_documents()
        # no users yet, let's create default one
        if not cnt_users:
            default_user = User(name="admin", email="admin@localhost")
            default_user.set_password("123")
            await default_user.commit()

        email = request.form.get('email')
        password = request.form.get('password')
        user = await User.authenticate(email, password)
        if user:
            request.ctx.session['user_id'] = str(user.pk)
            return response.redirect('/admin/')
        else:
            errors.append("Wrong email or password")
    return {"errors": errors, "hide_menu": True}
