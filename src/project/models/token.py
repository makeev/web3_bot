from dataclasses import dataclass

from umongo import Document, fields

from app import get_app
from utils.common import add_timestamp

app = get_app()


@dataclass
class Chain:
    chain_id: int
    node_url: str
    name: str


CHAINS = {
    1: Chain(
        chain_id=1,
        name='Ethereum',
        node_url=app.config.ETH_HTTP_NODE_URL,
    ),
    137: Chain(
        chain_id=137,
        name='Polygon',
        node_url=app.config.POLYGON_HTTP_NODE_URL,
    ),
}


@app.ctx.umongo.register
@add_timestamp
class Token(Document):
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
