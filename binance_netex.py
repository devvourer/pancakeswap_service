from web3 import Web3

import json
import requests

bsc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc))


koko_address = '0x7320c128e89bA4584Ab02ed1C9c96285b726443C'


def get_abi(address):
    url_eth = "https://api.bscscan.com/api"
    contract_address = web3.toChecksumAddress(address)
    api_endpoint = url_eth + "?module=contract&action=getabi&address=" + str(contract_address)
    r = requests.get(url=api_endpoint)
    response = r.json()
    abi = json.loads(response['result'])
    return abi


def get_contract_token(address: str):
    contract_address = web3.toChecksumAddress(address)
    abi = get_abi(address)
    sell_token_contract = web3.eth.contract(contract_address, abi=abi)
    return sell_token_contract

#
# contract = get_contract_token(koko_address)
#
# address_hold = web3.toChecksumAddress('0x7320c128e89ba4584ab02ed1c9c96285b726443c')
# balance = contract.functions.balanceOf(address_hold).call()
#
# print(web3.fromWei(balance, 'ether'))
