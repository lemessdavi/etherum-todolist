import json
from web3 import Web3
from flask import Flask
from solcx import compile_standard, install_solc
import os
from dotenv import load_dotenv
from web3.middleware import geth_poa_middleware

load_dotenv()

with open("./TaskContract.sol", "r") as file:
    task_contract_file = file.read()

print("Installing...")
install_solc("0.8.15")

print(task_contract_file)

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"TaskContract.sol": {"content": task_contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.8.15",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

bytecode = compiled_sol["contracts"]["TaskContract.sol"]["TaskContract"]["evm"][
    "bytecode"
]["object"]

abi = json.loads(
    compiled_sol["contracts"]["TaskContract.sol"]["TaskContract"]["metadata"]
)["output"]["abi"]

w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
chain_id = 1337

if chain_id == 4:
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    print(w3.clientVersion)

#manda dinheiro aqui, vai dar mt certo!
my_address = "0xAA5129041C4cc33c6280733DF5BB6FDaDA9207C9"
private_key = "0x36181fe80f7b573e781e8d854d4677e33ab161612eea0e57abfd2b819d7370fd"

app = Flask(__name__)

# Criar o contrato aqui
TaskContract = w3.eth.contract(abi=abi, bytecode=bytecode)

# Implantar o contrato na blockchain
nonce = w3.eth.get_transaction_count(my_address)
transaction = TaskContract.constructor().build_transaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt.contractAddress

# Instanciar o contrato implantado
task_contract = w3.eth.contract(address=contract_address, abi=abi)

@app.route('/api/test', methods=['GET'])
def test():
    return 'it works'

@app.route('/api/getTasks', methods=['GET'])
def getTask():
    return json.dumps(task_contract.functions.getMyTasks().call())

@app.route('/api/addTask/<text>', methods=['POST'])
def addTask(text):
    nonce = w3.eth.get_transaction_count(my_address)
    greeting_transaction = task_contract.functions.addTask(text, False, False).build_transaction(
        {
            "chainId": chain_id,
            "gasPrice": w3.eth.gas_price,
            "from": my_address,
            "nonce": nonce,
        }
    )
    signed_greeting_txn = w3.eth.account.sign_transaction(
        greeting_transaction, private_key=private_key
    )
    tx_greeting_hash = w3.eth.send_raw_transaction(signed_greeting_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_greeting_hash)
    return 'Task created successfully!'

@app.route('/api/deleteTask/<id>/<b>', methods=['POST'])
def deleteTask(id, b):
    nonce = w3.eth.get_transaction_count(my_address)
    tx_hash = task_contract.functions.deleteTask(int(id), bool(b)).transact(
        {"from": my_address, "nonce": nonce}
    )
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return "Task deleted successfully"


@app.route('/api/checkTask/<id>/<b>', methods=['POST'])
def checkTask(id, b):
    nonce = w3.eth.get_transaction_count(my_address)
    tx_hash = task_contract.functions.checkTask(int(id), bool(b)).transact(
        {"from": my_address, "nonce": nonce}
    )
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return "Task checked successfully"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
