#!/usr/bin/env python

import asyncio
import time
from decimal import Decimal

import click

from app import get_app
from project.models import Transaction, CHAINS
from utils import myjson
from utils.common import init_sanic_app


async def main(chain_id):
    app = get_app()
    await init_sanic_app(app)

    chain = CHAINS.get(chain_id)
    if not chain:
        raise Exception('chain with id %d not found' % chain_id)

    w3 = chain.get_web3_instance()
    is_connected = await w3.isConnected()

    print('is_connected: %s' % is_connected)

    # uniswap router
    router_address = chain.uniswap_v2_router  # @TODO или брать из параметров cli

    last_block = None
    while True:
        pending_block = await w3.eth.get_block("pending", full_transactions=True)
        if pending_block['number'] != last_block:
            print('new block %s' % pending_block['number'])
            last_block = pending_block['number']
            for transaction in pending_block['transactions']:
                if transaction['to'] != router_address:
                    continue

                transaction_exists = await Transaction.find_one({
                    "chain_id": 137, "hash": transaction['hash'].hex(),
                })
                if transaction_exists:
                    continue

                t = await Transaction.from_tx_dict(transaction, chain_id, decode_cotnract_input=True)
                await t.commit()

                print('new transaction {explorer_url}/tx/{hash}'.format(explorer_url=chain.explorer_url, hash=t.hash))
        else:
            # @TODO поставить 1s когда будет более дорогая нода
            await asyncio.sleep(5)


if __name__ == '__main__':
    @click.command()
    @click.option('--chain_id', type=int, required=True, prompt=True)
    def run(chain_id):
        asyncio.run(main(chain_id))

    run()

