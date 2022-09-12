import json
from copy import copy
from decimal import Decimal

from umongo import Document, fields

from project.models.chain import ChainMixin
from utils import myjson
from utils.myjson import dumps

from app import get_app
from utils.common import add_timestamp

app = get_app()


@app.ctx.umongo.register
@add_timestamp
class Transaction(ChainMixin, Document):
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
        indexes = [
            'status', 'value', 'value_decimal', 'contract_function',
            'from_', 'to', 'block_hash', 'block_number',
            {'key': ['hash', 'chain_id'], 'unique': True},
        ]

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

    def pretty_param(self, value, known_addresses):
        if isinstance(value, int) and value > 10 ** 10:
            return app.ctx.w3.fromWei(value, 'ether')

        if isinstance(value, list):
            return [self.pretty_param(v, known_addresses) for v in value]

        if isinstance(value, str) and value.startswith('0x'):
            return "<a href='{explorer_url}/address/{address}' target='_blank'>{name}</a>".format(
                address=value,
                name=known_addresses.get(value, value),
                explorer_url=self.chain.explorer_url,
            )

        if isinstance(value, str) and len(value) > 50 and value.startswith('b'):
            return '...bytes...'

        return value

    async def get_w3_contract(self, force_create=False):
        """
        Вытаскиваем контракт, если у нас есть abi
        """
        from project.models import Contract

        if not self.to:
            return

        contract = await Contract.get_by_address(self.to, self.chain_id)
        if not contract and force_create:
            # создаем контракт и пытаемся достать abi
            contract = Contract(
                name='created for %s' % self.to,
                address=self.to,
                chain_id=self.chain_id
            )
            contract.abi = contract.get_abi(default=None)
            await contract.commit()

        if contract:
            # если есть abi, то вернет web3.Contract
            return contract.get_w3_contract()

    @classmethod
    async def from_tx_dict(cls, tx, chain_id: int, decode_cotnract_input=True):
        """
        Создает объект Transaction из того что присылает блокчейн,
        может попытаться достать данные по методу контракта, если decode_cotnract_input=True
        """
        t = cls(
            block_hash=tx['blockHash'].hex(),
            block_number=tx['blockNumber'],
            hash=tx['hash'].hex(),
            from_=tx['from'],
            to=tx['to'],
            input=tx['input'],
            gas=tx['gas'],
            gas_price=str(tx['gasPrice']),
            nonce=str(tx['nonce']),
            value=str(tx['value']),
            value_decimal=Decimal(Decimal(tx['value']) / 10 ** 18),
            type=tx['type'],
            v=tx['v'],
            r=tx['r'].hex(),
            s=tx['s'].hex(),
            chain_id=chain_id
        )

        if decode_cotnract_input:
            # ищем контракт, если нет в базе пытаемся вытащить через api(force_create=True)
            w3_contract = await t.get_w3_contract(force_create=True)
            if w3_contract:
                try:
                    func_obj, func_params = w3_contract.decode_function_input(t.input)
                    t.contract_function = func_obj.fn_name
                    t.contract_params = myjson.dumps(func_params)
                except ValueError as e:
                    print("can't decode input data" % e)

        return t
