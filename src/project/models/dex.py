from dataclasses import dataclass

from uniswap import Uniswap

from app import get_app
from project.models import ChainMixin
from utils.zerox import ZeroXProtocol

app = get_app()


@dataclass
class Dex(ChainMixin):
    name: str
    chain_id: int
    factory_address: str
    router_address: str
    uniswap_version: int
    _uniswap_instance: Uniswap

    def get_uniswap_instance(self, address=None, private_key=None):
        if not self._uniswap_instance:
            self._uniswap_instance = Uniswap(
                version=self.uniswap_version, web3=self.chain.get_web3_instance(),
                # нам не нужен кошелек, чтобы просто посмотреть цену
                address=address, private_key=private_key,
                # uniswap-python не знает адреса в polygon, там это quickswap
                factory_contract_addr=self.factory_address,
                router_contract_addr=self.router_address,
            )

        return self._uniswap_instance

    @staticmethod
    def token_to_address(token):
        if hasattr(token, 'address'):
            return token.address

        return str(token)

    async def get_price_input(self, token_from, token_to, amount_bpt: int) -> int:
        token_from = self.token_to_address(token_from)
        token_to = self.token_to_address(token_to)

        if self.uniswap_version:
            # uniswap like dex
            client = self.get_uniswap_instance()
            return client.get_price_input(token_from, token_to, amount_bpt)

        if self.name.startswith('0x'):  # 0x protocol
            async with ZeroXProtocol() as zx:
                r = await zx.price(sellToken=token_from, buyToken=token_to, sellAmount=amount_bpt)
                data = await r.json()
                return int(data['buyAmount'])

        # @TODO ничего не нашли?
        return 0


DEXS = {
    1: {
        "uniswap_v2": Dex(
            name="Uniswap V3",
            chain_id=1,
            uniswap_version=2,
            factory_address=None,
            router_address=None,
            _uniswap_instance=None,
        ),
        "uniswap_v3": Dex(
            name="Uniswap V3",
            chain_id=1,
            uniswap_version=3,
            factory_address=None,
            router_address=None,
            _uniswap_instance=None,
        ),
    },
    137: {
        "uniswap_v2": Dex(
            name="Uniswap V2 (Quickswap)",
            chain_id=137,
            uniswap_version=2,
            factory_address='0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32',
            router_address='0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff',
            _uniswap_instance=None,
        ),
        "uniswap_v3": Dex(
            name="Uniswap V3",
            chain_id=137,
            uniswap_version=3,
            factory_address=None,
            router_address=None,
            _uniswap_instance=None,
        ),
        "zx": Dex(
            name="0x protocol",
            chain_id=137,
            uniswap_version=None,
            factory_address=None,
            router_address=None,
            _uniswap_instance=None,
        )
    }
}
