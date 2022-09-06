from dataclasses import dataclass

from uniswap import Uniswap

from app import get_app
from project.models import ChainMixin

app = get_app()


@dataclass
class Dex(ChainMixin):
    name: str
    chain_id: int
    factory_address: str
    router_address: str
    uniswap_version: int
    _uniswap_instance: object

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


DEXS = {
    1: {
        "uniswap_v2": Dex(
            name="Uniswap V3",
            chain_id=1,
            uniswap_version=2,
            factory_address='',
            router_address='',
            _uniswap_instance=None,
        ),
        "uniswap_v3": Dex(
            name="Uniswap V3",
            chain_id=1,
            uniswap_version=3,
            factory_address='',
            router_address='',
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
            factory_address='',
            router_address='',
            _uniswap_instance=None,
        ),
    }
}
