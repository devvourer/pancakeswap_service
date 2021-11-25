import json
import requests
import time

from utils import is_same_address
from web3 import Web3

bsc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc))

print(web3.isConnected())

pan_router_contract_address = '0x10ED43C718714eb63d5aA57B78B54704E256024E'


BUSD = web3.toChecksumAddress('0xe9e7cea3dedca5984780bafc599bd69add087d56')
BNB = web3.toChecksumAddress('0xB8c77482e45F1F44dE1745F52C74426C631bDD52')
ETH = web3.toChecksumAddress('0x0000000000000000000000000000000000000000')
ETH_B = web3.toChecksumAddress('0x2170ed0880ac9a755fd29b2688956bd959f933f8')

class Bsc:

    def __init__(self, address: str = None, private_key: str = None):
        if address:
            self.address = address
            self.private_key = private_key
            self.balance = web3.eth.get_balance(address)
            self.nonce = web3.eth.get_transaction_count(self.address)

        self.selfcontract = self._get_contract_token(pan_router_contract_address)

    @staticmethod
    def _get_abi(address):
        url_eth = "https://api.bscscan.com/api"
        contract_address = web3.toChecksumAddress(address)
        api_endpoint = url_eth + "?module=contract&action=getabi&address=" + str(contract_address)
        r = requests.get(url=api_endpoint)
        response = r.json()
        abi = json.loads(response['result'])
        return abi

    def _get_price_input(
            self,
            token0,
            token1,
            qty,
            route: str = None,
            fee: int = None,
    ):
        if fee == None:
            fee = 3000

        weth = self.contract.functions.WETH().call()
        price = self.contract.functions.getAmountsOut(
            qty,
            [weth, token1]
        ).call()[-1]

        return price

    def _get_contract_token(self, address: str):
        contract_address = web3.toChecksumAddress(address)
        abi = self._get_abi(address)
        sell_token_contract = web3.eth.contract(contract_address, abi=abi)
        return sell_token_contract

    def sell_token(self, contract_id, amount):
        sell_token_contract = self._get_contract_token(contract_id)
        token_value = web3.toWei(amount, 'ether')
        # token_value2 = web3.fromWei(amount, 'ether')
        # start = time.time()

        approve = sell_token_contract.functions.approve(
            pan_router_contract_address, self.balance
        ).buildTransaction({
            'from': self.address,
            'gasPrice': web3.toWei('5', 'gwei'),
            'nonce': self.nonce,
        })

        signed_txn = web3.eth.account.sign_transaction(approve, private_key=self.private_key)
        tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        time.sleep(10)

        pancakeswap2_txn = self.contract.functions.swapExactTokensForEth(
            token_value, 0,
            [contract_id, BUSD],
            self.address,
            (int(time.time()) + 1000000)
        ).buildTransaction({
            'from': self.address,
            'gasPrice': web3.toWei('5', 'gwei'),
            'nonce': self.nonce,
        })

        signed_txn = web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=self.private_key)
        tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        return tx_token

    def buy_token(self, token_to_buy, amount):
        token_to_buy = web3.toChecksumAddress(token_to_buy)
        pancakeswap2_txn = self.contract.functions.swapExactETHForTokens(
            0,
            [BUSD, token_to_buy],
            self.address,
            (int(time.time()) + 10000)
        ).buildTransaction({
            'from': self.address,
            'value': web3.toWei(amount, 'ether'),
            'gas': 250000,
            'gasPrice': web3.toWei('5', 'gwei'),
            'nonce': self.nonce
        })
        signed_txn = web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=self.private_key)
        tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        return tx_token

    def add_liquidity(self, token_address, value):
        token_contract = self._get_contract_token(token_address)

        wbnb = web3.toChecksumAddress('0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c')

        total_supply = token_contract.functions.totalSupply().call
        approve = token_contract.functions.approve(pan_router_contract_address, total_supply).buildTransaction({
            'from': self.address,
            'gasPrice': web3.toWei('5', 'gwei'),
            'nonce': self.nonce,
        })
        signed_tx = web3.eth.account.sign_transaction(approve, private_key=self.private_key)
        tx_token = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        time.sleep(10)

        amount_token_desired = web3.toWei('90000000', 'ether')
        amount_token_min = web3.toWei('90000000', 'ether')
        amount_eth_min = 19000000000000000
        deadline = int(time.time()) + 1000000

        addliquid = token_contract.functions.addLiquidityETH(
            token_address, amount_token_desired, amount_token_min,
            amount_eth_min, self.address, deadline
        ).buildTransaction({
            'from': self.address,
            'value': web3.toWei(value, 'ether'),
            'gasPrice': web3.toWei('5', 'gwei'),
            'nonce': self.nonce,
        })

        signed_txn = web3.eth.account.sign_transaction(addliquid, private_key=self.private_key)
        tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        return tx_token



    def remove_liquidity(self,  sender_address, token_address, liquid_contract_address):
        wbnb = web3.toChecksumAddress("0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c")  # WBNB

        liquid_contract = self._get_contract_token(liquid_contract_address)
        liquid_total_supply = liquid_contract.functions.totalSupply().call()

        balance_liquid = liquid_contract.functions.balanceOf(sender_address, liquid_total_supply).call()
        time.sleep(5)

        amount_wbnb_min = 1399000000000000
        amount_token_address_min = 6435730000000000000000000
        deadline = int(time.time()) + 1000000

        approve = liquid_contract.functions.approve(pan_router_contract_address, balance_liquid).buildTransaction({
            'from': sender_address,
            'gasPrice': web3.toWei('10', 'gwei'),
            'nonce': web3.eth.get_transaction_count(sender_address),
        })
        signed_tx = web3.eth.account.sign_transaction(approve, private_key=self.private_key)
        tx_token = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        time.sleep(10)

        remove = liquid_contract.functions.removeLiquidity(
            wbnb, token_address, balance_liquid, amount_wbnb_min,
            amount_token_address_min, sender_address, deadline
        ).buildTransaction({
            'from': sender_address,
            'gasPrice': web3.toWei('10', 'gwei'),
            'nonce': self.nonce
        })

        signed_txn = web3.eth.account.sign_transaction(remove, private_key=self.private_key)
        tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return tx_token

    def get_currency(self, token_address):
        currency = Web3.toChecksumAddress(token_address)
        currency_rate = self._get_price_input(BNB, currency, 1)
        busd_rate = self._get_price_input(BNB, BUSD, 1)
        conversion = ((1 / currency_rate) * (busd_rate / 1))
        return f'{conversion}'


