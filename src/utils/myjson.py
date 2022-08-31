import decimal
import json
from functools import partial


class BlockchainEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)

        if isinstance(obj, int):
            return str(obj)

        if isinstance(obj, bytes):
            return str(obj)

        return json.JSONEncoder.default(self, obj)


dumps = partial(json.dumps, cls=BlockchainEncoder)
