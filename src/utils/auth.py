from bson import ObjectId
from sanic.exceptions import Forbidden

import settings


async def get_logged_in_user(request):
    from project.models import User

    user_id = request.ctx.session.get('user_id')
    user = await User.find_one({"id": ObjectId(user_id)})
    return user


def token_required(f):
    async def wrapper(request, *args, **kwargs):
        token = request.headers.get('x-auth-token')
        if settings.AUTH_TOKEN and token != settings.AUTH_TOKEN:
            raise Forbidden()

        return await f(request, *args, **kwargs)
    return wrapper