import json
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.future import transaction
from pyteal import compileTeal, Mode
from contract import approval_program, clear_state_program
from deployment_functions import *
from helper_functions import *

# Opening JSON file with testing data for convenience purposes
f = open('credentials.json')
 
# returns JSON object as a dictionary
data = json.load(f)

app_id = data["app_id"]
asset_id = data["asset_id"]
application_address = data["application_address"]
test_address = data["test_address"]
test_mnemonic = data["test_mnemonic"]
test_private_key = mnemonic.to_private_key(test_mnemonic)
# Closing file
f.close()


# connection parameters
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

# initialize an algodClient
algod_client = algod.AlgodClient(algod_token, algod_address)


# if test account is not opted in, call opt_in_app() with 
# the test user's private key and the app_id as an argument
if not is_opted_in_app(algod_client, test_address, app_id):

    # opt into application from test account
    result = opt_in_app(algod_client, test_private_key, app_id)

    # print result confirmation transaction confirmation 
    print_confirmation(result)


# Example 1: makes a single AssetTxn with provided asset_id 
# The transaction takes three arguments: 
# app_args[0] = b"deposit" (bytes)
# app_args[1] = b"AssetTxn" (bytes)
# app_args[2] = amount to send (int) 

# caveat: if app_args[1] == b"AssetTxn", the foreign assets 
# array must have the asset_id in it 
app_args = [b"deposit", b"AssetTxn", 1]

call_app(algod_client, 
        test_private_key, 
        app_id, 
        app_args,
        rekey_to=application_address,
        foreign_assets=[asset_id]
        )

# Example 2: makes a single PaymentTxn 
# The transaction takes three arguments: 
# app_args[0] = b"deposit" (bytes)
# app_args[1] = b"PaymentTxn" (bytes)
# app_args[2] = amount to send (int) 

# caveat: if app_args[1] == b"PaymentTxn", the foreign assets 
# array must be None
app_args = [b"deposit", b"PaymentTxn", 1]

call_app(algod_client, 
        test_private_key, 
        app_id, 
        app_args,
        rekey_to=application_address,
        foreign_assets=None
        )

# asset holdings for test user and application address
print("Asset holding for user address: ")
print_asset_holding(algod_client, test_address, asset_id)

print("Asset holding for smart contract address: ")
print_asset_holding(algod_client, application_address, asset_id)


# algo holdings for test user and application address
account_info = algod_client.account_info(test_address)
print("Account balance test user: {} microAlgos".format(account_info.get('amount')) + "\n")

account_info = algod_client.account_info(application_address)
print("Account balance application address: {} microAlgos".format(account_info.get('amount')) + "\n")


# if you wish to verify the test user's account has been rekeyed properly, 
# run the function below

payment_txn(algod_client, test_private_key, test_address)