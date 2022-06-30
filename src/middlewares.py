import ujson

from app import get_app
from sanic import response
from utils.auth import get_logged_in_user
from project.models import UserLog

app = get_app()


@app.middleware("request")
async def context_middleware(request):
    request.ctx.foo = 'bar'


@app.middleware("request")
async def login_check_middleware(request):
    # @TODO
    if request.path != '/admin/login' \
            and request.path != '/admin/debug' \
            and request.path != '/' \
            and not request.path.startswith('/static') \
            and not request.path.startswith('/i/'):
        user = await get_logged_in_user(request)
        if not user:
            return response.redirect(app.url_for("admin.user_login"))
        else:
            # log user actions
            log = UserLog(
                user=user,
                action=request.method,
                path=request.path,
                details=ujson.dumps(dict(request.form))
            )
            await log.commit()
