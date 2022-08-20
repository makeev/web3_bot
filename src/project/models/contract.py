from umongo import Document, fields

from app import get_app

app = get_app()


_CONTRACTS_CACHE = {}


@app.ctx.umongo.register
class Contract(Document):
    name = fields.StrField()
    address = fields.StrField(unique=True)
    abi = fields.StrField()

    class Meta:
        indexes = ['address']

    @classmethod
    async def get_by_address(cls, address):
        contract = _CONTRACTS_CACHE.get(address)

        if not contract:
            contract = await cls.find_one({"address": address})
            if contract:
                _CONTRACTS_CACHE[address] = contract

        return contract

    def get_w3_contract(self, w3):
        return w3.eth.contract(address=self.address, abi=self.abi)
