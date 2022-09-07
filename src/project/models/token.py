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

    _CACHE = {}

    class Meta:
        indexes = [
            'is_active',
            'symbol',
            'chain_id',
            {'key': ['symbol', 'chain_id'], 'unique': True},
            {'key': ['address', 'chain_id'], 'unique': True},
        ]

    @classmethod
    async def get_by_address_n_chain(cls, address, chain_id):
        chain_id = int(chain_id)
        token = cls._CACHE.get(chain_id, {}).get(address)

        if not token:
            token = await cls.find_one({
                "address": address,
                "chain_id": chain_id
            })

            if token:
                cls._CACHE.setdefault(chain_id, {})[address] = token

        return token
