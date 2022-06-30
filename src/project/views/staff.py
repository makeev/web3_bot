import json
from datetime import datetime
from sanic.__version__ import __version__

from app import get_app, jinja
from utils.common import get_real_ip

app = get_app()


def hide_secret(s):
    if s:
        return '*' * len(s[:-4]) + s[-4:]


@jinja.template("staff.html")
async def staff_view(request):
    headers = {}

    for key, value in request.headers.items():
        headers[key] = value

    if request.method == "POST":
        action = request.form.get('action')
        if action == "truncate_table":
            table = request.form.get("table_name")
            collection = app.ctx.motor_db[table]
            await collection.delete_many({})
        elif action == "drop_table":
            table = request.form.get("table_name")
            collection = app.ctx.motor_db[table]
            await collection.drop()

    return {
        "current_tz_time": datetime.now(),
        "DEBUG": app.config.DEBUG,
        "sanic_version": __version__,
        "headers": json.dumps(headers, indent=2),
        "get_real_ip": get_real_ip(request),
    }
