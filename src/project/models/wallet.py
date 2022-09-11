from umongo import Document, fields
from web3 import Web3

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
    tokens = fields.DictField()

    # кешируем балансы, чтобы не дергать ноду каждый раз
    balances = fields.DictField()

    # адреса которые заапрувили, чтобы не слать транзакцию каждый раз
    approved_addresses = fields.DictField()

    async def get_token_balance(self, symbol, chain_id):
        chain = CHAINS.get(chain_id)
        w3 = chain.get_web3_instance()

        if symbol == chain.currency_symbol:
            # баланс нативных токенов можем вернуть так
            return await w3.eth.get_balance(self.address)

        # ищем токен, нам нужен адрес и abi
        token = await Token.find_one({"symbol": symbol, "chain_id": chain_id})
        if not token or not token.abi:
            return None

        contract = token.get_w3_contract()
        return contract.functions.balanceOf(self.address).call()

    @property
    def balances_html(self):
        balances_list = []
        for chain_name, balances in self.balances.items():
            for data in balances:
                balances_list.append("%s: %s %s" % (chain_name, data['amount'], data['symbol']))

        return "<br>".join(balances_list)

    async def approve(self, token: Token, spender_address, chain_id: int):
        contract = token.get_w3_contract()
        chain = CHAINS[chain_id]
        w3 = chain.get_web3_instance()

        spender = Web3.toChecksumAddress(spender_address)
        # апрувим сразу максимально возможное количество,
        # не безопасно, зато удобно
        max_amount = Web3.toWei(2**64 - 1, 'ether')
        nonce = w3.eth.getTransactionCount(self.address)

        tx = contract.functions.approve(spender, max_amount).buildTransaction({
            'from': self.address,
            'nonce': nonce
        })
        print(tx)

        signed_tx = w3.eth.account.signTransaction(tx, self.private_key)
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

        print("Approve", w3.toHex(tx_hash))

        return w3.eth.wait_for_transaction_receipt(tx_hash)
