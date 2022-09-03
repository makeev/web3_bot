from dataclasses import dataclass

from app import get_app

app = get_app()


@dataclass
class Chain:
    chain_id: int
    node_url: str
    name: str
    explorer_url: str
    is_poa: bool
    uniswap_v2_router: str


CHAINS = {
    1: Chain(
        chain_id=1,
        name='Ethereum',
        node_url=app.config.ETH_HTTP_NODE_URL,
        explorer_url="https://etherscan.io",
        is_poa=False,
        uniswap_v2_router='0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
    ),
    137: Chain(
        chain_id=137,
        name='Polygon',
        node_url=app.config.POLYGON_HTTP_NODE_URL,
        explorer_url="https://polygonscan.com",
        is_poa=True,
        uniswap_v2_router='0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff'
    ),
}
