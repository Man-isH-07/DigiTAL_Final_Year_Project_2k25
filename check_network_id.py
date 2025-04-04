# check_network_id.py
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
print(f"Connected: {w3.is_connected()}")
print(f"Network ID: {w3.eth.chain_id}")