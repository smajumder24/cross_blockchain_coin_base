from solcx import compile_standard, install_solc
import json
import os
from web3 import Web3
import sha3
import time
from eth_abi.packed import encode_packed
from hexbytes import HexBytes
import numpy as np

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

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

install_solc("0.8.18")

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

coin_abi = json.loads(
    compiled_coin_sol["contracts"]["Coin.sol"]["Coin"]["metadata"]
)["output"]["abi"]

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

relay_abi = json.loads(
    compiled_relay_sol["contracts"]["Relay.sol"]["Relay"]["metadata"]
)["output"]["abi"]

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

cctransfer_abi = json.loads(
    compiled_cctransfer_sol["contracts"]["CCTransfer.sol"]["CCTransfer"]["metadata"]
)["output"]["abi"]

# load the key and address data from the json file
data_file = open('keys_and_addresses.json')
data = json.load(data_file)
n = data["n"]
t = data["t"]
coin_address = data["coin_address"]
relay_address = data["relay_address"]
cctransfer_address = data["cctransfer_address"]

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
node_address = w3.eth.accounts[0]
node_private_key = private_keys[0]

deployed_coin_contract = w3.eth.contract(coin_address, abi=coin_abi)
deployed_relay_contract = w3.eth.contract(relay_address, abi=relay_abi)
deployed_cctransfer_contract = w3.eth.contract(cctransfer_address, abi=cctransfer_abi)

### CREATE CC TRANSFER REQUEST ###

print("Create cross-chain transfer request...")
add_request_nonce = w3.eth.get_transaction_count(node_address)
deployed_cctransfer_contract.functions.addIncomingRequest(1000,node_address).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": add_request_nonce})
print(f"Done! Added cross-chain request")

num_requests = deployed_cctransfer_contract.functions.getNumberOfRequests().call()
print(f"Number of requests = {num_requests}")
latest_index = num_requests - 1

### VOTE TO APPROVE THE REQUEST ###

# print(deployed_cctransfer_contract)
# message = encode_packed(['address', 'uint'], [cctransfer_address, latest_index])
# print(message.hex())
# k = sha3.keccak_256()
# k.update(message)
# print("test hash: "+k.hexdigest())

# contract_bytes = deployed_relay_contract.functions.getBytes(cctransfer_address, latest_index).call()
# print(f"contract bytes = {contract_bytes.hex()}")

# contract_hash = deployed_relay_contract.functions.getHash(cctransfer_address, latest_index).call()
# print(f"contract hash = {contract_hash.hex()}")

# signed_message =  w3.eth.account._sign_hash(k.digest(), private_key=private_keys[0])
# print(signed_message)
# signature = signed_message["signature"]

signing_start_time = time.time()

message = encode_packed(['address', 'uint'], [cctransfer_address, latest_index])
k = sha3.keccak_256()
k.update(message)

merged_signature_list = []

for i in range(n-t):
    signed_message =  w3.eth.account._sign_hash(k.digest(), private_key=private_keys[0])
    merged_signature_list += signed_message["signature"]

merged_signature = bytearray(merged_signature_list)
print("merged signature: "+merged_signature.hex())

signing_end_time = time.time()
print("time cost of signing:", (signing_end_time - signing_start_time))

addvote_relay_nonce = w3.eth.get_transaction_count(w3.eth.accounts[0])
deployed_relay_contract.functions.approve(cctransfer_address,latest_index,merged_signature).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": w3.eth.accounts[0], "nonce": addvote_relay_nonce})

# print(f"Adding n - t = {n-t} votes to the Relay contract...")
# for i in range(n-t):
#     print(f"Adding vote for node {i}...")
#     addvote_relay_nonce = w3.eth.get_transaction_count(w3.eth.accounts[i])
#     deployed_relay_contract.functions.approve(cctransfer_address,latest_index).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": w3.eth.accounts[i], "nonce": addvote_relay_nonce})

#     is_approved = deployed_relay_contract.functions.isApproved(cctransfer_address,latest_index).call()
#     print(f"Approved = {is_approved}")
# print(f"Done! Added votes to the Relay contract")

### COMMIT THE REQUEST ###

print("Commit the cross-chain transfer request...")
commit_request_nonce = w3.eth.get_transaction_count(node_address)
deployed_cctransfer_contract.functions.commitRequest(latest_index).transact({"chainId": chain_id, "gasPrice": w3.eth.gas_price, "from": node_address, "nonce": commit_request_nonce})
print(f"Done! Committed the cross-chain transfer request")

balance = deployed_coin_contract.functions.balanceOf(node_address).call()
print(f"Balance of node 0: {balance}")

end_time = time.time()
print("time duration:", (end_time - start_time))