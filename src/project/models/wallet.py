from umongo import Document, fields

from app import get_app
from project.models import CHAINS, Token
from utils.common import add_timestamp

app = get_app()


@app.ctx.umongo.register
@add_timestamp
class Wallet(Document):
    name = fields.StrField()
    address = fields.StrField()
    private_key = fields.StrField()

    # мы должны знать какие токены у нас храняться, чтобы вернуть баланс
    # т.к. баланс не нативных токенов хранится на контракте токена, а не кошелька
    tokens = fields.ListField(fields.StrField())
    # кешируем балансы, чтобы не дергать ноду каждый раз
    balances = fields.DictField()

    async def get_token_balance(self, symbol, chain_id):
        chain = CHAINS.get(chain_id)
        w3 = chain.get_web3_instance()

        if symbol == chain.currency_symbol:
            # баланс нативных токенов можем вернуть так
            return w3.eth.get_balance(self.address)

        # ищем токен, нам нужен адрес и abi
        token = await Token.find_one({"symbol": symbol, "chain_id": chain_id})
        if not token or not token.abi:
            return None

        contract = token.get_w3_contract()
        return contract.functions.balanceOf(self.address).call()
