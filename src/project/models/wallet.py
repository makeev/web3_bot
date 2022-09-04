from umongo import Document, fields

from app import get_app
from project.models import CHAINS
from utils.common import add_timestamp

app = get_app()


@app.ctx.umongo.register
@add_timestamp
class Wallet(Document):
    name = fields.StrField()
    address = fields.StrField()
    private_key = fields.StrField()

    def get_token_balance(self, symbol, chain_id):
        chain = CHAINS.get(chain_id)
        w3 = chain.get_web3_instance()

        if symbol == chain.currency_symbol:
            # баланс нативных токенов можем вернуть так
            return w3.eth.get_balance(self.address)

        # чтобы вернуть баланс кастомного токена - надо знать abi контракта
        # @TODO
