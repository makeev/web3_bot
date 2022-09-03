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
    is_connected = w3.isConnected()

    print('is_connected: %s' % is_connected)

    # uniswap router
    router_address = chain.uniswap_v2_router  # @TODO или брать из параметров cli

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
                    value_decimal=Decimal(Decimal(transaction['value'])/10**18),
                    type=transaction['type'],
                    v=transaction['v'],
                    r=transaction['r'].hex(),
                    s=transaction['s'].hex(),
                    chain_id=chain.chain_id
                )

                contract = await t.get_contract(w3)
                if contract:
                    try:
                        func_obj, func_params = contract.decode_function_input(t.input)
                        t.contract_function = func_obj.fn_name
                        print(func_params)
                        t.contract_params = myjson.dumps(func_params)
                    except ValueError as e:
                        print('something wrong with contract %s' % e)

                await t.commit()

                print('new transaction {explorer_url}/tx/{hash}'.format(explorer_url=chain.explorer_url, hash=t.hash))
        else:
            # @TODO поставить 1s когда будет более дорогая нода
            time.sleep(5)


if __name__ == '__main__':
    @click.command()
    @click.option('--chain_id', type=int, required=True, prompt=True)
    def run(chain_id):
        asyncio.run(main(chain_id))

    run()

