from dataclasses import dataclass

from web3 import Web3, HTTPProvider, AsyncHTTPProvider
from web3.eth import AsyncEth
from web3.middleware import geth_poa_middleware, async_geth_poa_middleware
from web3.net import AsyncNet

from app import get_app
from utils.scan import ScanApi

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
    uniswap_v2_factory: str
    uniswap_v2_router: str
    currency_symbol: str
    _web3: object

    def get_web3_instance(self):
        if not self._web3:
            self._web3 = Web3(
                AsyncHTTPProvider(self.node_url),
                modules={'eth': (AsyncEth,), 'net': (AsyncNet,)},
                middlewares=[]
            )
            blocked_w3 = Web3(HTTPProvider(self.node_url))

            if self.is_poa:
                self._web3.middleware_onion.inject(async_geth_poa_middleware, layer=0)
                blocked_w3.middleware_onion.inject(geth_poa_middleware, layer=0)

            # account и contract еще не реализован в async версии
            self._web3.eth.account = blocked_w3.eth.account
            self._web3.eth.contract = blocked_w3.eth.contract

        return self._web3

    @property
    def scan_api(self):
        return ScanApi(api_endpoint=self.scan_api_url, api_key=self.scan_api_key)


CHAINS = {
    1: Chain(
        chain_id=1,
        name='Ethereum',
        node_url=app.config.ETH_HTTP_NODE_URL,
        explorer_url="https://etherscan.io",
        scan_api_url="https://api.etherscan.io/api",
        scan_api_key=app.config.ETHERSCAN_API_KEY,
        is_poa=False,
        uniswap_v2_factory='0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
        uniswap_v2_router='0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
        currency_symbol='ETH',
        _web3=None,
    ),
    137: Chain(
        chain_id=137,
        name='Polygon',
        node_url=app.config.POLYGON_HTTP_NODE_URL,
        explorer_url="https://polygonscan.com",
        scan_api_url="https://api.polygonscan.com/api",
        scan_api_key=app.config.POLYGONSCAN_API_KEY,
        is_poa=True,
        uniswap_v2_factory='0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32',
        uniswap_v2_router='0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff',
        currency_symbol='MATIC',
        _web3=None,
    ),
}


class ChainMixin:
    @property
    def chain(self) -> Chain:
        return CHAINS.get(self.chain_id)
