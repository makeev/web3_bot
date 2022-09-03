from dataclasses import dataclass

from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

from app import get_app

app = get_app()


@dataclass
class Chain:
    chain_id: int
    node_url: str
    name: str
    explorer_url: str
    scan_api_url: str
    scan_api_key: str
    is_poa: bool
    uniswap_v2_router: str
    _web3: object

    def get_web3_instance(self):
        if not self._web3:
            self._web3 = Web3(HTTPProvider(self.node_url))
            if self.is_poa:
                self._web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        return self._web3


CHAINS = {
    1: Chain(
        chain_id=1,
        name='Ethereum',
        node_url=app.config.ETH_HTTP_NODE_URL,
        explorer_url="https://etherscan.io",
        scan_api_url="https://api.etherscan.io/api",
        scan_api_key=app.config.ETHERSCAN_API_KEY,
        is_poa=False,
        uniswap_v2_router='0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
        _web3=None
    ),
    137: Chain(
        chain_id=137,
        name='Polygon',
        node_url=app.config.POLYGON_HTTP_NODE_URL,
        explorer_url="https://polygonscan.com",
        scan_api_url="https://api.polygonscan.com/api",
        scan_api_key=app.config.POLYGONSCAN_API_KEY,
        is_poa=True,
        uniswap_v2_router='0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff',
        _web3=None
    ),
}


class ChainMixin:
    @property
    def chain(self) -> Chain:
        return CHAINS.get(self.chain_id)
