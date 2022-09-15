from decimal import Decimal

from umongo import Document, fields
from umongo.validate import OneOf

from app import get_app
from project.models import Token, Transaction, DEXS
from project.models.chain import ChainMixin, CHAINS
from utils.common import add_timestamp, MyEnum
from utils.wei_converter import from_basis_points

app = get_app()


@app.ctx.umongo.register
@add_timestamp
class Deal(ChainMixin, Document):
    class Types(MyEnum):
        USD_ARB = 'usd_arb'

    tx_hash = fields.StrField()
    chain_id = fields.IntField()
    type = fields.StrField(validate=OneOf(Types.choices()))
    sell_token = fields.ReferenceField(Token)
    buy_token = fields.ReferenceField(Token)
    sell_amount = fields.StrField()
    buy_amount = fields.StrField()
    tx_fee_usd = fields.StrField()
    profit_usd = fields.StrField()

    @property
    def total_profit_usd(self):
        return Decimal(self.profit_usd)

    @classmethod
    async def get_or_create_from_transaction(cls, type: str, tx_hash: str, chain_id: int, save=False):
        """
        Чтобы создать и посчитать сделку, нам нужна транзакция.
        Зная тип Deal мы можем декодировать данные отправленные в смарт контракт
        и посчитать наш профит.
        """
        chain = CHAINS[chain_id]

        deal = await Deal.find_one({"tx_hash": tx_hash, "chain_id": chain_id})
        if deal:
            return deal

        # сначала ищем транзакцию
        t = await Transaction.find_one({"hash": tx_hash, "chain_id": chain_id})
        if not t:
            w3 = chain.get_web3_instance()
            # в базе нет такой транзакции, достаем из блокчейна
            tx = await w3.eth.get_transaction(tx_hash)
            if not tx:
                raise Exception('tx %s not found in chain %s' % (tx_hash, chain.name))

            # декодируем и сохраняем транзакцию в базу
            t = await Transaction.from_tx_dict(tx, chain_id, decode_cotnract_input=True)
            await t.commit()

        if type == cls.Types.USD_ARB.value:
            assert t.contract_function == 'transformERC20'
            assert t.params is not None

            sell_token = await Token.get_by_address_n_chain(t.params['inputToken'], chain_id=chain_id)
            buy_token = await Token.get_by_address_n_chain(t.params['outputToken'], chain_id=chain_id)

            # в случае USD_ARB арбитража, нормальная цена и есть цена в долларах
            sell_amount = from_basis_points(t.params['inputTokenAmount'], decimals=sell_token.decimals)
            buy_amount = from_basis_points(t.params['minOutputTokenAmount'], decimals=buy_token.decimals)

            # считаем gas в базовой валюте блокчейна
            tx_fee = int(t.gas) * int(t.gas_price)

            # переводим в usd, чтобы посчитать профит
            uniswap = DEXS[chain_id]['uniswap_v3']
            USDC = await Token.get_by_symbol_n_chain("USDC", chain_id)
            tx_fee_usd = from_basis_points(await uniswap.get_price_input('WMATIC', USDC, tx_fee), decimals=USDC.decimals)
            profit_usd = buy_amount - sell_amount - tx_fee_usd

            deal = cls(
                tx_hash=t.hash,
                chain_id=chain_id,
                type=type,
                sell_token=sell_token,
                buy_token=buy_token,
                sell_amount=str(sell_amount),
                buy_amount=str(buy_amount),
                tx_fee_usd=str(tx_fee_usd),
                profit_usd=str(profit_usd)
            )
            if save:
                await deal.commit()
            return deal
        else:
            raise Exception('unknown Deal type')

