import json

from algosdk import account, logic, constants
from algosdk.future import transaction
from helper_functions import wait_for_confirmation, print_created_asset, print_asset_holding



# create new application
def create_app(
    client,
    private_key,
    approval_program,
    clear_program,
    global_schema,
    local_schema,
):
    # define sender as creator
    sender = account.address_from_private_key(private_key)

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()
    
    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(
        sender,
        params,
        on_complete,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
    )

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]
    print("Created new app-id:", app_id)

    return app_id



# opt-in to application
def opt_in_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)
    print("OptIn from account: ", sender)

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = transaction.ApplicationOptInTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    result = wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("OptIn to app-id:", transaction_response["txn"]["txn"]["apid"])
    
    return result



# call application
def call_app(client, private_key, index, app_args, rekey_to, foreign_assets):
    # declare sender
    sender = account.address_from_private_key(private_key)
    print("Call from account:", sender)

    # get node suggested parameters
    params = client.suggested_params()
    params.fee = 3 * constants.MIN_TXN_FEE

    # create unsigned transaction
    txn = transaction.ApplicationNoOpTxn(sender, 
                                        params, 
                                        index, 
                                        app_args, 
                                        rekey_to=rekey_to,
                                        foreign_assets=foreign_assets)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    result = wait_for_confirmation(client, tx_id)

    return result


# delete application
def delete_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = transaction.ApplicationDeleteTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    result = wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Deleted app-id:", transaction_response["txn"]["txn"]["apid"])

    return result 



def update_app(client, private_key, app_id, approval_program, clear_program):

    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = transaction.ApplicationUpdateTxn(
                                        sender,
                                        params,
                                        app_id,
                                        approval_program,
                                        clear_program,
                                        app_args=None,
                                        accounts=None,
                                        foreign_apps=None,
                                        foreign_assets=None,
                                        note=None,
                                        lease=None,
                                        rekey_to=None)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    result = wait_for_confirmation(client, tx_id)

    # display results
    #transaction_response = client.pending_transaction_info(tx_id)
    
    # application address
    application_address = logic.get_application_address(app_id)

    print("Application was modified with app_id:", app_id, "and with application address:", application_address)

    return application_address



# close out from application
def close_out_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = transaction.ApplicationCloseOutTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    result = wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Closed out from app-id: ", transaction_response["txn"]["txn"]["apid"])

    return result 



# clear application
def clear_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = transaction.ApplicationClearStateTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    result = wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Cleared app-id:", transaction_response["txn"]["txn"]["apid"])

    return result 


# create an asset 
def create_asset(client, private_key):

    # declare sender
    sender = account.address_from_private_key(private_key)

    params = client.suggested_params()

    txn = transaction.AssetConfigTxn(
        sender=sender,
        sp=params,
        total=1_000_000_000,
        default_frozen=False,
        unit_name="C3pio",
        asset_name="C3coin",
        manager=None,
        reserve=sender,
        freeze=None,
        clawback=None,
        strict_empty_address_check=False,
        url=None, 
        decimals=0)

    # Sign with secret key of creator
    stxn = txn.sign(private_key)

    # Send the transaction to the network and retrieve the txid.
    
    txid = client.send_transaction(stxn)
    print("Signed transaction with txID: {}".format(txid))
    # Wait for the transaction to be confirmed
    confirmed_txn = wait_for_confirmation(client, txid)  
    print("TXID: ", txid)
    print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))   

    
    # Retrieve the asset ID of the newly created asset by first
    # ensuring that the creation transaction was confirmed,
    # then grabbing the asset id from the transaction.
    print("Transaction information: {}".format(
        json.dumps(confirmed_txn, indent=4)))
    # print("Decoded note: {}".format(base64.b64decode(
    #     confirmed_txn["txn"]["txn"]["note"]).decode()))
    try:
        # Pull account info for the creator
        ptx = client.pending_transaction_info(txid)
        asset_id = ptx["asset-index"]
        print_created_asset(client, private_key, asset_id)
        print_asset_holding(client, private_key, asset_id)
    except Exception as e:
        print(e)

    return asset_id


