# C3 Bounty

### Single AssetTxn explanation: 

  1) The user sends an ApplicationCallTxn to the smart contract with 3 app_args: ["deposit", "AssetTxn", amount].
     The rekey_to is set to the Application Address and the foreign_assets array contains the asset to be sent. 
  2) If the smart contract is not opted in to the asset, **the opt_in_smart_contract_to_asa()** subroutine is called
     which opts the smart contract to the ASA. After the smart contract is opted in to the ASA, the **asset_transfer()** 
     subroutine is called, which sends the asset from the user account to the smart contract and rekeys the account back to the user. 
     Otherwise, if the smart contract is already opted in to the ASA, only the **asset_transfer()** subroutine is called. 
