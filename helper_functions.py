import base64
from algosdk import mnemonic, encoding
from algosdk.future import transaction
import json

# helper function to compile program source
def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])


# helper function that converts a mnemonic passphrase into a private signing key
def get_private_key_from_mnemonic(mn):
    private_key = mnemonic.to_private_key(mn)
    return private_key


# helper function that waits for a given txid to be confirmed by the network
def wait_for_confirmation(client, txid):
    last_round = client.status().get("last-round")
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get("confirmed-round") and txinfo.get("confirmed-round") > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print(
        "Transaction {} confirmed in round {}.".format(
            txid, txinfo.get("confirmed-round")
        )
    )
    return txinfo


def wait_for_round(client, round):
    last_round = client.status().get("last-round")
    print(f"Waiting for round {round}")
    while last_round < round:
        last_round += 1
        client.status_after_block(last_round)
        print(f"Round {last_round}")


def format_state(state):
    formatted = {}
    for item in state:
        key = item["key"]
        value = item["value"]
        formatted_key = base64.b64decode(key).decode("utf-8")
        if value["type"] == 1:
            # byte string
            if formatted_key == "voted":
                formatted_value = base64.b64decode(value["bytes"]).decode("utf-8")
            else:
                formatted_value = value["bytes"]
            formatted[formatted_key] = formatted_value
        else:
            # integer
            formatted[formatted_key] = value["uint"]
    return formatted


# read user local state
def read_local_state(client, addr, app_id):
    results = client.account_info(addr)
    for local_state in results["apps-local-state"]:
        if local_state["id"] == app_id:
            if "key-value" not in local_state:
                return {}
            return format_state(local_state["key-value"])
    return {}


# read app global state
def read_global_state(client, addr, app_id):
    results = client.account_info(addr)
    apps_created = results["created-apps"]
    for app in apps_created:
        if app["id"] == app_id:
            try:
                #print(app["params"]["global-state"])
                
                return format_state(app["params"]["global-state"])
            except KeyError: 
                return "No global state at this time."
    return {}


# convert 64 bit integer i to byte string
def intToBytes(i):
    return i.to_bytes(8, "big")



def print_confirmation(result):
    print("Result confirmed in round: {}".format(result['confirmed-round']))



def print_single_log(log):
    
    # integer
    strlog = base64.b64decode(log)
    integer = int(strlog.hex(), 16)

    # string
    try: 
        formatted_value = base64.b64decode(log).decode('UTF-8')

    except UnicodeDecodeError:

        base_64_decoded_address = base64.b64decode(log.encode())

        if len(bytearray(base_64_decoded_address)) == 32:
            formatted_value = encoding.encode_address(base_64_decoded_address)

        elif len(bytearray(base_64_decoded_address)) == 58:
            formatted_value = base_64_decoded_address.decode()

        else:
            formatted_value = log.encode()

    # print
    dictionary = {"Int": integer, "String": formatted_value}

    print(dictionary) 



def print_logs(result):
    try:
        print("\nLogs:\n")
        for log in result['logs']:
            print_single_log(log)
        print()
    except KeyError: 
        print("No logs during this runtime.\n")


# returns true if the account has opted into the application, false otherwise
def is_opted_in_app(algod_client, user_address, app_id):
    account_info = algod_client.account_info(user_address)
    for a in account_info['apps-local-state']:
        if a['id'] == app_id:
            return True
    return False



#   Utility function used to print created asset for account and assetid
def print_created_asset(algodclient, account, assetid):    
    import json
    account_info = algodclient.account_info(account)
    idx = 0
    for my_account_info in account_info['created-assets']:
        scrutinized_asset = account_info['created-assets'][idx]
        idx = idx + 1       
        if (scrutinized_asset['index'] == assetid):
            print("Asset ID: {}".format(scrutinized_asset['index']))
            print(json.dumps(my_account_info['params'], indent=4))
            break


def print_asset_holding(algodclient, account, assetid):
    import json
    account_info = algodclient.account_info(account)
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx = idx + 1        
        if (scrutinized_asset['asset-id'] == assetid):
            print("Asset ID: {}".format(scrutinized_asset['asset-id']))
            print(json.dumps(scrutinized_asset, indent=4))
            break


def transfer_asset(algodclient, test_private_key, test_address, application_address, asset_id):
    #creator_private_key = mnemonic.to_private_key(creator_mnemonic)
    params = algodclient.suggested_params()

    # Use the AssetTransferTxn class to transfer assets and opt-in
    txn = transaction.AssetTransferTxn(
        sender=test_address,
        sp=params,
        receiver=application_address,
        amt=1,
        index=asset_id)
        
    stxn = txn.sign(test_private_key)
       
    txid = algodclient.send_transaction(stxn)
    # Wait for the transaction to be confirmed
    confirmed_txn = wait_for_confirmation(algodclient, txid) 
    print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))    

    print_asset_holding(algodclient, test_address, asset_id)


def payment_txn(algodclient, private_key, address):

    # build transaction
    params = algodclient.suggested_params()

    receiver = "HZ57J3K46JIJXILONBBZOHX6BKPXEM2VVXNRFSUED6DKFD5ZD24PMJ3MVA"
    amount = 1

    unsigned_txn = transaction.PaymentTxn(address, params, receiver, amount, None)

    # sign transaction
    signed_txn = unsigned_txn.sign(private_key)

    # submit transaction
    txid = algodclient.send_transaction(signed_txn)

    # wait for confirmation 
   
    result = wait_for_confirmation(algodclient, txid)  
   

    print("Transaction information: {}".format(json.dumps(result, indent=4)))