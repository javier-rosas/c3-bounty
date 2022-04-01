# C3 Bounty

## This smart contract is able to handle both AssetTxn's and PaymentTxn's. 

### Single AssetTxn explanation: 

  1) The user sends an ApplicationCallTxn to the smart contract with 3 app_args: ["deposit", "AssetTxn", amount].
     The rekey_to field is set to the Application Address and the foreign_assets array contains the ASA to be sent. 
  2) If the smart contract is not opted in to the asset, **the opt_in_smart_contract_to_asa()** subroutine is called
     which opts the smart contract to the ASA. After the smart contract is opted in to the ASA, the **asset_transfer()** 
     subroutine is called, which sends the specified amount of the ASA from the user account to the smart contract and rekeys 
     the account back to the user. If the smart contract is already opted in to the ASA, only the **asset_transfer()** subroutine is called. 
     
### Single PaymentTxn explanation: 

  1) The user sends an ApplicationCallTxn to the smart contract with 3 app_args: ["deposit", "PaymentTxn", amount] with the 
     rekey_to field is set to the Application Address.  
  3) The smart contract calls **inner_payment_transaction** subroutine, which sends the specified amount of Algos from the user 
     account to the smart contract and rekeys the account back to the user. 

### How to run the code: 

  1) Simply run the **contract_execution.py** file. For convienience, this code has a test user and a test ASA which are used to send 
     a single AssetTxn to the smart contract. The code also demonstrates a single PaymentTxn to the smart contract. 
