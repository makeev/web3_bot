from umongo import Document, fields

from app import get_app
from utils.common import add_timestamp

app = get_app()


@app.ctx.umongo.register
@add_timestamp
class Token(Document):
    name = fields.StrField()
    address = fields.StrField()
    symbol = fields.StrField(unique=True)
    decimals = fields.IntField()
    logo_uri = fields.StrField()
    extensions = fields.DictField()
    is_active = fields.BoolField(default=False)

    class Meta:
        indexes = ['is_active', 'symbol']
