from decimal import Decimal

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

    contract_function = fields.StrField(allow_none=True)
    contract_params = fields.StrField(allow_none=True)
    status = fields.StrField(allow_none=True)

    @property
    def value_decimal(self):
        return Decimal(Decimal(self.value)/10**18)

    async def get_contract(self, w3):
        """
        Вытаскиваем контракт, если у нас есть abi
        """
        from project.models import Contract

        if not self.to:
            return

        contract = await Contract.get_by_address(self.to)
        if contract:
            return contract.get_w3_contract(w3)
