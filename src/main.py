import time
from pprint import pprint

from web3 import Web3, HTTPProvider

from settings import ETH_HTTP_NODE_URL


def main(name):
    w3 = Web3(HTTPProvider(ETH_HTTP_NODE_URL))
    is_connected = w3.isConnected()
    print('is_connected: %s' % is_connected)

    # uniswap
    router_address = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
    factory_address = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'

    last_block = None
    while True:
        pending_block = w3.eth.get_block("pending", full_transactions=True)
        if pending_block['number'] != last_block:
            print('new block %s' % pending_block['number'])
            last_block = pending_block['number']
            for transaction in pending_block['transactions']:
                if transaction['to'] == router_address:
                    pprint(transaction)
                    break
        else:
            time.sleep(1)

    # while True:
    #     new_entries = filter.get_all_entries()
    #     print(new_entries)
    #     time.sleep(0.5)


if __name__ == '__main__':
    main('PyCharm')

