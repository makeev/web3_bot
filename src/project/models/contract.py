from typing import Optional

import aiohttp
from umongo import Document, fields

from app import get_app
from project.models.chain import ChainMixin

app = get_app()


_CONTRACTS_CACHE = {}


@app.ctx.umongo.register
class Contract(ChainMixin, Document):
    name = fields.StrField()
    address = fields.StrField()
    abi = fields.StrField(allow_none=True)
    chain_id = fields.IntField()

    class Meta:
        indexes = [
            'address',
            {'key': ['address', 'chain_id'], 'unique': True},
        ]

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

    async def get_abi(self) -> Optional[str]:
        """
        Достает abi контракта через api, если контракт верифицирован
        """
        async with aiohttp.ClientSession() as session:
            params = {
                "module": "contract",
                "action": "getabi",
                "address": self.address,
                "apikey": self.chain.scan_api_key
            }
            r = await session.get(self.chain.scan_api_url, params=params)
            assert r.status == 200
            data = await r.json()
            if data['message'] == 'OK':
                return data['result']
