import os
import solcx
from web3 import Web3
from web3.exceptions import ConnectionError, TransactionNotFound
from dotenv import load_dotenv

load_dotenv()

# Set solc version
if '0.8.0' not in solcx.get_installed_solc_versions():
    solcx.install_solc('0.8.0')
solcx.set_solc_version('0.8.0')

# Compile
with open('../contracts/EcoLoanCertifier.sol', 'r') as f:
    source = f.read()
compiled_sol = solcx.compile_source(source, output_values=['abi', 'bin'])
contract_interface = compiled_sol['<stdin>:EcoLoanCertifier']

# Connect
rpc_url = os.getenv('RPC_URL', 'https://testnet.hashio.io/api')
w3 = Web3(Web3.HTTPProvider(rpc_url))
chain_id = 296

private_key = os.getenv('HEDERA_PRIVATE_KEY')
address = os.getenv('HEDERA_EVM_ADDRESS')

if not w3.is_connected():
    raise ConnectionError(f"Failed to connect to RPC: {rpc_url}. Try Arkhia alternative.")

# Deploy
EcoLoanCertifier = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
nonce = w3.eth.get_transaction_count(address)
gas_price = w3.eth.gas_price  # Dynamic, updated for 2026 fluctuations
estimated_gas = EcoLoanCertifier.constructor().estimate_gas({'from': address})
tx = EcoLoanCertifier.constructor().build_transaction({
    'chainId': chain_id,
    'gasPrice': gas_price,
    'gas': estimated_gas * 12 // 10,  # 20% buffer
    'nonce': nonce,
    'from': address
})

signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
print(f"Tx sent: {tx_hash.hex()}")

try:
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)  # Longer timeout for testnet
    contract_addr = tx_receipt.contractAddress
    print(f"Deployed at: {contract_addr}")
    # Update .env with ECO_CONTRACT_ADDRESS={contract_addr}
except Exception as e:
    print(f"Error: {e}. Check HashScan or balance.")
