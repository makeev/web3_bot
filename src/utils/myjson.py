from functools import partial

import ujson


dumps = partial(ujson.dumps, reject_bytes=False)
