import time
import asyncio

from web3 import Web3, HTTPProvider
from app import get_app
from utils.common import init_sanic_app

from project.models import Transaction
from settings import ETH_HTTP_NODE_URL


async def main():
    app = get_app()
    await init_sanic_app(app)

    w3 = Web3(HTTPProvider(ETH_HTTP_NODE_URL))
    is_connected = w3.isConnected()
    print('is_connected: %s' % is_connected)

    # uniswap router
    router_address = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'

    last_block = None
    while True:
        pending_block = w3.eth.get_block("pending", full_transactions=True)
        if pending_block['number'] != last_block:
            print('new block %s' % pending_block['number'])
            last_block = pending_block['number']
            for transaction in pending_block['transactions']:
                if transaction['to'] != router_address:
                    continue

                t = Transaction(
                    block_hash=transaction['blockHash'].hex(),
                    block_number=transaction['blockNumber'],
                    hash=transaction['hash'].hex(),
                    from_=transaction['from'],
                    to=transaction['to'],
                    input=transaction['input'],
                    gas=transaction['gas'],
                    gas_price=str(transaction['gasPrice']),
                    nonce=str(transaction['nonce']),
                    value=str(transaction['value']),
                    type=transaction['type'],
                    v=transaction['v'],
                    r=transaction['r'].hex(),
                    s=transaction['s'].hex()
                )
                await t.commit()
                print('new transaction https://etherscan.io/tx/{hash}'.format(hash=t.hash))
        else:
            # @TODO поставить 1s когда будет более дорогая нода
            time.sleep(5)


if __name__ == '__main__':
    asyncio.run(main())

