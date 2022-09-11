from eth_utils import to_checksum_address

from project.models import Wallet, CHAINS


async def zx_swap_token_to_token(wallet: Wallet, quote):
    """
    Меняем токен через 0x protocol
    :quote: - то что приходит от метода /quote api 0x protocol
    :returns: tx_hash
    """
    chain = CHAINS[quote['chainId']]
    w3 = chain.get_web3_instance()
    nonce = await w3.eth.get_transaction_count(wallet.address)

    tx = {
        "from": to_checksum_address(wallet.address),
        "to": to_checksum_address(quote['to']),
        "data": quote['data'],
        "value": 0,
        "gas": int(quote['gas']),
        "gasPrice": int(quote['gasPrice']),
        # 'maxFeePerGas': w3.toWei(250, 'gwei'),
        # 'maxPriorityFeePerGas': w3.toWei(100, 'gwei'),
        "nonce": nonce,
        "chainId": quote['chainId']
    }

    # sign the transaction
    signed_tx = w3.eth.account.sign_transaction(tx, wallet.private_key)

    # send transaction
    return await w3.eth.send_raw_transaction(signed_tx.rawTransaction)
