import json
from copy import copy
from decimal import Decimal

from umongo import Document, fields
from utils.myjson import dumps

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
    value_decimal = fields.DecimalField()
    type = fields.StrField()
    v = fields.IntField()
    r = fields.StrField()
    s = fields.StrField()

    contract_function = fields.StrField(allow_none=True)
    contract_params = fields.StrField(allow_none=True)
    status = fields.StrField(allow_none=True)
    chain_id = fields.IntField()

    class Meta:
        collection_name = 'transactions'
        indexes = ['status', 'value', 'value_decimal', 'contract_function',
                   'from_', 'to', 'block_hash', 'block_number']

    @property
    def params(self):
        if self.contract_params:
            return json.loads(self.contract_params)

    def pretty_params(self, known_addresses={}):
        if not self.params:
            return ''

        params = copy(self.params)
        for key, value in self.params.items():
            params[key] = self.pretty_param(value, known_addresses)

        return dumps(params, indent=2)

    @classmethod
    def pretty_param(cls, value, known_addresses):
        if isinstance(value, int) and value > 10**10:
            return app.ctx.w3.fromWei(value, 'ether')

        if isinstance(value, list):
            return [cls.pretty_param(v, known_addresses) for v in value]

        if isinstance(value, str) and value.startswith('0x'):
            return "<a href='https://etherscan.io/address/{address}' target='_blank'>{name}</a>".format(address=value, name=known_addresses.get(value, value))

        if isinstance(value, str) and len(value) > 50 and value.startswith('b'):
            return '...bytes...'

        return value

    async def get_contract(self):
        """
        Вытаскиваем контракт, если у нас есть abi
        """
        from project.models import Contract

        if not self.to:
            return

        contract = await Contract.get_by_address(self.to)
        if contract:
            return contract.get_w3_contract()
