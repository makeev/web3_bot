import json
from typing import Optional

import web3
from umongo import Document, fields
from web3 import Web3
from web3.exceptions import ABIFunctionNotFound

from app import get_app
from project.models.chain import ChainMixin

app = get_app()


_CONTRACTS_CACHE = {}

# This is a simplified Contract Application Binary Interface (ABI) of an ERC-20 Token Contract.
# It will expose only the methods: balanceOf(address), decimals(), symbol(), name() and totalSupply()
simplified_abi = json.dumps([
    {
        'inputs': [{'internalType': 'address', 'name': 'account', 'type': 'address'}],
        'name': 'balanceOf',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    },
    {
        'inputs': [],
        'name': 'decimals',
        'outputs': [{'internalType': 'uint8', 'name': '', 'type': 'uint8'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    },
    {
        'inputs': [],
        'name': 'symbol',
        'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    },
    {
        'inputs': [],
        'name': 'name',
        'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    },
    {
        'inputs': [],
        'name': 'totalSupply',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    }
])


class ContractAbiMixin:
    async def get_abi(self, default=simplified_abi) -> Optional[str]:
        """
        Достает abi контракта через api, если контракт верифицирован.
        Или возвращает упрощенный контракт(simplified_abi подходит только для ERC20 контрактов),
        для всяких там роутеров и прокси надо указывать default=None
        @TODO эту вермишель надо переписать
        """
        async with self.chain.scan_api as api:
            data = await api.call("contract", "getsourcecode", address=self.address)
            if data['message'] != 'OK':
                return default

            if data['result'][0]['Proxy'] == '1':
                # это прокси контракт, надо искать имплементацию
                data = await api.call("contract", "getabi", address=data['result'][0]['Implementation'])
                if data['message'] != 'OK':
                    return default

                return data['result']

            abi = data['result'][0]['ABI']
            # проверяем ABI, иногда api не правильно возвращает прокси
            # или возвращает не контракт
            w3 = self.chain.get_web3_instance()
            try:
                contract = w3.eth.contract(
                    address=Web3.toChecksumAddress(self.address),
                    abi=abi
                )
            except ValueError:
                return default

            try:
                contract.functions.symbol().call()
            except ABIFunctionNotFound:
                # нет такой функции, значит ищем прокси
                try:
                    implementation = contract.functions.implementation().call()
                    data = await api.call("contract", "getabi", address=implementation)
                    assert data['message'] == 'OK'
                    return data['result']
                except:
                    return default
            else:
                # все ок
                return abi

    def get_w3_contract(self) -> Optional[web3.eth.Contract]:
        if self.abi:
            w3 = self.chain.get_web3_instance()
            return w3.eth.contract(address=Web3.toChecksumAddress(self.address), abi=self.abi)


@app.ctx.umongo.register
class Contract(ContractAbiMixin, ChainMixin, Document):
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
    async def get_by_address(cls, address, chain_id):
        key = '%d_%s' % (chain_id, address)
        contract = _CONTRACTS_CACHE.get(key)

        if not contract:
            contract = await cls.find_one({"address": address, "chain_id": chain_id})
            if contract:
                _CONTRACTS_CACHE[key] = contract

        return contract
