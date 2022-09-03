from umongo import Document, fields

from app import get_app
from project.models import ChainMixin
from utils.common import add_timestamp

app = get_app()


@app.ctx.umongo.register
@add_timestamp
class Token(ChainMixin, Document):
    name = fields.StrField()
    address = fields.StrField()
    symbol = fields.StrField()
    decimals = fields.IntField()
    logo_uri = fields.StrField()
    is_active = fields.BoolField(default=False)
    chain_id = fields.IntField()

    class Meta:
        indexes = [
            'is_active',
            'symbol',
            'chain_id',
            {'key': ['symbol', 'chain_id'], 'unique': True},
        ]
