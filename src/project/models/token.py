from umongo import Document, fields
from web3 import Web3
from web3.exceptions import ABIFunctionNotFound

from app import get_app
from project.models import ChainMixin, ContractAbiMixin
from utils.common import add_timestamp

app = get_app()


@app.ctx.umongo.register
@add_timestamp
class Token(ContractAbiMixin, ChainMixin, Document):
    name = fields.StrField()
    address = fields.StrField()
    symbol = fields.StrField()
    decimals = fields.IntField()
    logo_uri = fields.StrField()
    is_active = fields.BoolField(default=False)
    chain_id = fields.IntField()
    abi = fields.StrField(allow_none=True)

    # основная монета, в которой не стыдно хранить сбережение(WETH, USDC, USDT,...)
    is_base_asset = fields.BoolField(default=False)
    # торгуется ли этот токен, т.е. есть ли ликвидность
    is_tradable = fields.BoolField(default=False)

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

    async def update_from_contract(self):
        # обновляем ABI
        self.abi = await self.get_abi()

        # создаем контракт с новым ABI
        contract = self.get_w3_contract()

        # получаем данные из контракта
        try:
            self.name = contract.functions.name().call()
            self.symbol = contract.functions.symbol().call()
            self.decimals = contract.functions.decimals().call()
            self.is_active = True
        except ABIFunctionNotFound:
            # ебаный контракт, помечаем как неактивный
            self.is_active = False

        await self.commit()

    def get_balance_for(self, address):
        # создаем контракт с новым ABI
        contract = self.get_w3_contract()
        return contract.functions.balanceOf(Web3.toChecksumAddress(address)).call()
