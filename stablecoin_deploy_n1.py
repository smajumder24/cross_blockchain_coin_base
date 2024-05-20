from solcx import compile_standard, install_solc
import json
import os
from web3 import Web3
import subprocess
import time
import re
import argparse

### INITIALIZE ###

# mnemonic: top bus drama shoulder build master apart arrange notice fancy truth ice
# 16 accounts

private_keys = [
    "0d9fb7ddd8a2e3c19b9c57166f6dce352c5c021fe79e6dd9654b3adfbfbaad26",
    "74e853dc72b18efb576929ccc84903c0d5044ee2445661e884033bf69eec2638",
    "d14fa190b8cbd656fa4f8fe9acbe531cc19ed8b80a39f1e40205816885f80753",
    "05f6739e9a66796ddb57310f2142b0534d10937a22475f744994ffc76953ce70",
    "9620e18cde7eae53c810ec7a80fd49e5b418dba6870958ed4f2ed15f2479022f",
    "57bee8409f420f3e8e7f1993b64f27fd6bc03368db749956550932304502a884",
    "0b087981241722083ebf113ef6d062f0b8af82c593cb92e3b3612ee54a2cece9",
    "dd45d7f2ce48c6aa6a61989eeac6ee744f371054ae89a1dc4982fe12a0d222ab",
    "1ae07aee2dede3a67e0f2e193e49481819d8701d9830e19bb57812c831ba963f",
    "f148c3fbdc45fa2554a97e7498b6112ab04ceeef87debb61b6624ce7fdee2e05",
    "d1ee0eadf33442ed9c61b6da201975d473dc0e019c172024caf6945040f78792",
    "a0fc20c4cb3b197716e42e4062a8a8e01cc5dd6759fe728fc2c5880a3573e494",
    "e000975a7ba4b2c010d0e98850632b1510cd7858a2db0ef9019370cce7cff5ce",
    "3855a3046094b021b0710e1d9ae3987f82d91837ba326c698ac172d57a5c8e83",
    "7a169b606afaccdccc397e49a44d56a68a2cfbb7f8f544376658554409121728",
    "249705240d48de99e7272441057c93559fe0663538f7385a0581a1936310a939",
]

start_time = time.time()

# helpful: https://gist.github.com/BjornvdLaan/e41d292339bbdebb831d0b976e1804e8
# tether contract: https://etherscan.io/token/0xdac17f958d2ee523a2206206994597c13d831ec7#code

# see https://coinsbench.com/how-to-deploy-and-interact-with-solidity-contracts-with-python-and-ganache-be63334323e6

my_parser = argparse.ArgumentParser(description='Deploy the three contracts')
my_parser.add_argument('-n', action='store', type=int, required=True)
my_parser.add_argument('-t', action='store', type=int, required=True)
args = vars(my_parser.parse_args())

n = args["n"]
t = args["t"]

# sig_dir = "C:/Users/dani3/Dropbox/utwente backup/research/programmatuur/rust/multi-party-ecdsa/target/release/examples/";

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

install_solc("0.8.18")

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
node_address = w3.eth.accounts[0]
node_private_key = private_keys[0]

### DEPLOY COIN ###

with open(os.path.join(__location__, "Coin.sol"), "r") as file:
    coin_contract_file = file.read()

compiled_coin_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Coin.sol": {"content": coin_contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "metadata",
                        "evm.bytecode",
                        "evm.bytecode.sourceMap",
                    ]  # output needed to interact with and deploy contract
                }
            }
        },
    },
    solc_version="0.8.18",
)

with open(os.path.join(__location__, "compiler_output.json"), "w") as file:
    json.dump(compiled_coin_sol, file)

## get bytecode
coin_bytecode = compiled_coin_sol["contracts"]["Coin.sol"]["Coin"]["evm"][
    "bytecode"
]["object"]

# ## get abi
coin_abi = json.loads(
    compiled_coin_sol["contracts"]["Coin.sol"]["Coin"]["metadata"]
)["output"]["abi"]

# create the contract in Python
coin_contract = w3.eth.contract(abi=coin_abi, bytecode=coin_bytecode)
# get the latest transaction
coin_nonce = w3.eth.get_transaction_count(node_address)

# create a transaction that deploys the contract
deploy_coin_transaction = coin_contract.constructor(chain_id).build_transaction(
    {"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": coin_nonce}
)

# sign the transaction
signed_deploy_coin_transaction = w3.eth.account.sign_transaction(deploy_coin_transaction, private_key=node_private_key)
print(f"Start Deploying Coin Contract!")
# send the transaction
deploy_coin_transaction_hash = w3.eth.send_raw_transaction(signed_deploy_coin_transaction.rawTransaction)
# wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
deploy_coin_transaction_receipt = w3.eth.wait_for_transaction_receipt(deploy_coin_transaction_hash)
coin_address = deploy_coin_transaction_receipt.contractAddress
print(f"Done! Contract Coin deployed to {coin_address}")

### DEPLOY RELAY ###

with open(os.path.join(__location__, "Relay.sol"), "r") as file:
    relay_contract_file = file.read()

compiled_relay_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Relay.sol": {"content": relay_contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "metadata",
                        "evm.bytecode",
                        "evm.bytecode.sourceMap",
                    ]  # output needed to interact with and deploy contract
                }
            }
        },
    },
    solc_version="0.8.18",
)

with open(os.path.join(__location__, "compiler_output.json"), "w") as file:
    json.dump(compiled_relay_sol, file)

## get bytecode
relay_bytecode = compiled_relay_sol["contracts"]["Relay.sol"]["Relay"]["evm"][
    "bytecode"
]["object"]

# ## get abi
relay_abi = json.loads(
    compiled_relay_sol["contracts"]["Relay.sol"]["Relay"]["metadata"]
)["output"]["abi"]

# create the contract in Python
relay_contract = w3.eth.contract(abi=relay_abi, bytecode=relay_bytecode)
# get the latest transaction
relay_nonce = w3.eth.get_transaction_count(node_address)

# create a transaction that deploys the contract
deploy_relay_transaction = relay_contract.constructor().build_transaction(
    {"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": relay_nonce}
)

# sign the transaction
signed_deploy_relay_transaction = w3.eth.account.sign_transaction(deploy_relay_transaction, private_key=node_private_key)
print(f"Start Deploying Relay Contract!")
# send the transaction
deploy_relay_transaction_hash = w3.eth.send_raw_transaction(signed_deploy_relay_transaction.rawTransaction)
# wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
deploy_relay_transaction_receipt = w3.eth.wait_for_transaction_receipt(deploy_relay_transaction_hash)
relay_address = deploy_relay_transaction_receipt.contractAddress
print(f"Done! Contract Relay deployed to {relay_address}")

### DEPLOY CCTRANSFER ###

with open(os.path.join(__location__, "CCTransfer.sol"), "r") as file:
    cctransfer_contract_file = file.read()

compiled_cctransfer_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"CCTransfer.sol": {"content": cctransfer_contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": [
                        "abi",
                        "metadata",
                        "evm.bytecode",
                        "evm.bytecode.sourceMap",
                    ]  # output needed to interact with and deploy contract
                }
            }
        },
    },
    solc_version="0.8.18",
)

with open(os.path.join(__location__, "compiler_output.json"), "w") as file:
    json.dump(compiled_cctransfer_sol, file)

## get bytecode
cctransfer_bytecode = compiled_cctransfer_sol["contracts"]["CCTransfer.sol"]["CCTransfer"]["evm"][
    "bytecode"
]["object"]

# ## get abi
cctransfer_abi = json.loads(
    compiled_cctransfer_sol["contracts"]["CCTransfer.sol"]["CCTransfer"]["metadata"]
)["output"]["abi"]

# create the contract in Python
cctransfer_contract = w3.eth.contract(abi=cctransfer_abi, bytecode=cctransfer_bytecode)
# get the latest transaction
cctransfer_nonce = w3.eth.get_transaction_count(node_address)

# create a transaction that deploys the contract
deploy_cctransfer_transaction = cctransfer_contract.constructor(coin_address, relay_address).build_transaction(
    {"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": cctransfer_nonce}
)

# sign the transaction
signed_deploy_cctransfer_transaction = w3.eth.account.sign_transaction(deploy_cctransfer_transaction, private_key=node_private_key)
print(f"Start Deploying CCTransfer Contract!")
# send the transaction
deploy_cctransfer_transaction_hash = w3.eth.send_raw_transaction(signed_deploy_cctransfer_transaction.rawTransaction)
# wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
deploy_cctransfer_transaction_receipt = w3.eth.wait_for_transaction_receipt(deploy_cctransfer_transaction_hash)
cctransfer_address = deploy_cctransfer_transaction_receipt.contractAddress
print(f"Done! Contract CCTransfer deployed to {cctransfer_address}")

### ADD THE WARDS ###

print("Adding CCTransfer as ward to Coin using 'rely'...")
deployed_coin_contract = w3.eth.contract(coin_address, abi=coin_abi)
addward_nonce = w3.eth.get_transaction_count(node_address)
deployed_coin_contract.functions.rely(cctransfer_address).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": addward_nonce})
print(f"Done! CCTransfer added as ward to Coin")

# add n addresses as wards for relay

print(f"Adding the remaining {n-1} nodes to the Relay contract...")
deployed_relay_contract = w3.eth.contract(relay_address, abi=relay_abi)
for i in range(n):
    if i > 0:
        print(f"Adding node {i}...")
        addnode_relay_nonce = w3.eth.get_transaction_count(node_address)
        deployed_relay_contract.functions.addWard(w3.eth.accounts[i]).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": addnode_relay_nonce})
print(f"Done! Added nodes to the Relay contract")

### FINALIZE ###

# write the keys and addresses to a JSON file
dictionary = {
    "n": n,
    "t": t,
    "coin_address": coin_address,
    "relay_address": relay_address,
    "cctransfer_address": cctransfer_address,
}
json_object = json.dumps(dictionary, indent=4)
with open("keys_and_addresses.json", "w") as outfile:
    outfile.write(json_object)
    
end_time = time.time()
print("time duration:", (end_time - start_time))