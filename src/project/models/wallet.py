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
        """
        Чтобы смарт контракт(например DEX) мог тратить наши токены, надо дать
        ему разрешение на это.
        """
        contract = token.get_w3_contract()
        chain = CHAINS[chain_id]
        w3 = chain.get_web3_instance()

        spender = Web3.toChecksumAddress(spender_address)
        # разрешаем тратить сразу максимально возможное количество,
        # не безопасно, зато удобно, не надо каждый раз вызывать approve перед обменом
        max_amount = Web3.toWei(2**64 - 1, 'ether')
        nonce = w3.eth.getTransactionCount(self.address)

        tx = contract.functions.approve(spender, max_amount).buildTransaction({
            'from': self.address,
            'nonce': nonce
        })

        signed_tx = w3.eth.account.signTransaction(tx, self.private_key)
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

        # ждем пока все пройдет успешно
        return w3.eth.wait_for_transaction_receipt(tx_hash)

    async def approve_if_needed(self, token: Token, spender_address, chain_id: int):
        if not self.approved_addresses:
            self.approved_addresses = {}

        # approved_addresses[chain_id][token_symbol] = [..addresses..]
        self.approved_addresses.setdefault(str(chain_id), {})
        self.approved_addresses[str(chain_id)].setdefault(token.symbol, [])

        if spender_address not in self.approved_addresses[str(chain_id)]:
            # апрувим
            await self.approve(token, spender_address, chain_id)

            # сохраняем информацию, что данный адрес уже заапрувлен для данной сети и токена
            self.approved_addresses[str(chain_id)][token.symbol].append(spender_address)
            await self.commit()
