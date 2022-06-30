from umongo import Document, fields

from app import get_app
from utils.common import add_timestamp

app = get_app()


@app.ctx.umongo.register
@add_timestamp
class Transaction(Document):
    block_hash = fields.StrField()
    block_number = fields.IntField()
    hash = fields.StrField()

    from_ = fields.StrField()
    to = fields.StrField(allow_none=True)

    input = fields.StrField()

    gas = fields.IntField()
    gas_price = fields.StrField()
    nonce = fields.StrField()
    value = fields.StrField()
    type = fields.StrField()
    v = fields.IntField()
    r = fields.StrField()
    s = fields.StrField()
