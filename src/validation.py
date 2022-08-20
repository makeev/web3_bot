import orjson
from sanic import response
from webargs_sanic.sanicparser import SanicParser, HandleValidationError

from app import get_app

app = get_app()


class ValidationParser(SanicParser):
    DEFAULT_VALIDATION_STATUS = 400


# Return validation errors as JSON
@app.exception(HandleValidationError)
async def handle_validation_error(request, err):
    if hasattr(err, 'exc') and err.exc:
        errors = err.exc.messages
    else:
        errors = err.args[0]
    return response.json({"errors": errors}, status=400)


# @app.exception(FbApiValidationError)
# async def handle_validation_error(request, err):
#     """
#     Custom exception handler example
#     """
#     return response.json({"json": err.json, "text": err.text, "status": err.status}, status=400)


def valid_json(value):
    try:
        orjson.dumps(orjson.loads(value))
        return True
    except:
        return False


parser = ValidationParser()
use_args = parser.use_args
use_kwargs = parser.use_kwargs
