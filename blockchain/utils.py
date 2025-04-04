# blockchain/utils.py
from web3 import Web3
from .contract_details import CONTRACT_ADDRESS, CONTRACT_ABI
import os


# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# Check if connected
if not w3.is_connected():
    raise Exception("Failed to connect to Ganache")

# Load the contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# Account to interact with the blockchain
ACCOUNT_ADDRESS = os.getenv('ACCOUNT_ADDRESS')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')

def add_record_to_blockchain(data_hash, record_type, patient_email, doctor_id):
    # Build the transaction
    nonce = w3.eth.get_transaction_count(ACCOUNT_ADDRESS)
    txn = contract.functions.addRecord(
        data_hash,
        record_type,
        patient_email,
        doctor_id
    ).build_transaction({
        'from': ACCOUNT_ADDRESS,
        'nonce': nonce,
        'gas': 2000000,
        'gasPrice': w3.eth.gas_price
    })

    # Sign and send the transaction
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)  # Updated from rawTransaction to raw_transaction
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # Get the record ID from the event
    event = contract.events.RecordAdded().process_receipt(tx_receipt)
    record_id = event[0]['args']['recordId']
    return record_id, tx_hash.hex()

def get_record_from_blockchain(record_id):
    # Call the getRecord function
    data_hash, record_type, patient_email, doctor_id, timestamp = contract.functions.getRecord(record_id).call()
    return {
        'data_hash': data_hash,
        'record_type': record_type,
        'patient_email': patient_email,
        'doctor_id': doctor_id,
        'timestamp': timestamp
    }