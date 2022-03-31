from pyteal import *


def approval_program():

    @Subroutine(TealType.none)
    def global_safety_checks():

        return Seq([
            # assert only one transaction in the group 
            Assert( Global.group_size() == Int(1)                                   ),
            # assert there is only one argument: "deposit", "asset_id", "amount"
            Assert( Txn.application_args.length() == Int(3)                         ),
            # assert the accounts array is of size 1 (only the account sending the transaction)
            Assert( Txn.accounts.length() == Int(0)                                 ),
            # assert the applications array is of size 1 (only the smart contract we are making the transaction to)
            Assert( Txn.applications.length() == Int(0)                             ),
            # assert the asset close to is the global zero address
            Assert( Txn.asset_close_to() == Global.zero_address()                   ),
            # assert the algos close_remainer_to is the global zero address 
            Assert( Txn.close_remainder_to() == Global.zero_address()               ),
            # assert the account is rekeyed to the application address (we will rekey back after the transfer)
            Assert(Txn.rekey_to() == Global.current_application_address()),


            Return()

        ])

    '''
    Argument: asa id (uint64)
    Returns: None 

    Function makes an inner transaction that opts the smart contract to the ASA provided
    '''
    @Subroutine(TealType.none)
    def inner_payment_transaction(asa_id):
     
        return Seq([
        # assert the array of assets is of size 1 
        Assert( Txn.assets.length() == Int(0)                                   ),
        InnerTxnBuilder.Begin(),

            InnerTxnBuilder.SetFields({
                TxnField.type_enum : TxnType.AssetTransfer,
                TxnField.xfer_asset : asa_id,
                TxnField.asset_amount : Int(0),
                TxnField.asset_sender : Txn.sender(),
                TxnField.asset_receiver: Global.current_application_address(),
                TxnField.fee : Int(0),
                TxnField.rekey_to: Txn.sender()
            }),

        InnerTxnBuilder.Submit()
            
        ])


    @Subroutine(TealType.none)
    def transaction_with_rekey_for_payment_transaction():
        return Int(1)




    '''
    Argument: asa id (uint64), amount (uint64)
    Returns: None 

    Explanation: 

    Function makes an inner transaction from the sender to the smart contract. This 
    is possible because the sender has rekeyed its account to the smart contract.The 
    smart contract rekeys the account back to the sender. The inner transaction fees are
    all 0 because the first sender transaction pays for all the fees.  
    '''
    @Subroutine(TealType.none)
    def asset_transfer(asa_id, amount):
     

        return Seq([
        # assert the array of assets is of size 1 
        Assert( Txn.assets.length() == Int(1)                                   ),


        InnerTxnBuilder.Begin(),

            InnerTxnBuilder.SetFields({
                TxnField.type_enum : TxnType.AssetTransfer,
                TxnField.xfer_asset : asa_id,
                TxnField.asset_amount : amount,
                TxnField.asset_sender : Txn.sender(),
                TxnField.asset_receiver: Global.current_application_address(),
                TxnField.fee : Int(0),
                TxnField.rekey_to: Txn.sender()
                }),

        InnerTxnBuilder.Submit()

        ])

    '''
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.sender: Txn.sender(),
            TxnField.receiver: Global.current_application_address(),
            TxnField.amount: amount,
            TxnField.fee: Int(0),
            TxnField.rekey_to: Txn.sender(),  # rekey back to user
        }),
        InnerTxnBuilder.Submit(),
    '''
        
            
       


    '''
    Argument: asa id (uint64)
    Returns: None 

    Explanation: 

    If the smart contract is not opted in to the asset, this function makes an 
    inner transaction that opts the smart contract to the ASA in question. 
    '''
    @Subroutine(TealType.none)
    def opt_in_smart_contract_to_asa(asa_id):
     
        return Seq([
        
        InnerTxnBuilder.Begin(),

            InnerTxnBuilder.SetFields({
                TxnField.type_enum : TxnType.AssetTransfer,
                TxnField.xfer_asset : asa_id,
                TxnField.asset_amount : Int(0),
                TxnField.asset_sender : Global.current_application_address(),
                TxnField.asset_receiver: Global.current_application_address(),
                TxnField.fee : Int(6_000)
                }),

        InnerTxnBuilder.Submit()
            
        ])




    @Subroutine(TealType.none)
    def transaction_with_rekey_for_asa_transfer():

        asa_id = Btoi( Txn.application_args[1] )
        amount = Btoi( Txn.application_args[2] )
        smart_contract_asset_balance = AssetHolding.balance( Global.current_application_address(), asa_id ) 
        

        # if smart contract is not opted in to the asset, 
        # call smart_contract_opt_in_to_asa()
        return Seq([
            smart_contract_asset_balance,
            # returns Int(1) if the smart contract is not opted in to asset
            If( Not(smart_contract_asset_balance.hasValue()) ).
                # if smart contract is not opted in to the asset, 
                # send an opt in transaction for the asset
                Then( Seq( opt_in_smart_contract_to_asa(asa_id) ) )
                # transfer the asset to the smart contract with a rekey back to the sender
                #Then( Seq( asset_transfer(asa_id, amount)) )
            ])





    

        
    deposit = Seq([
        global_safety_checks(),
        transaction_with_rekey_for_asa_transfer(),
        Return(Int(1))
    ])

    program = Cond(

        [Txn.application_id() == Int(0), Return(Int(1))                         ],

        [Txn.on_completion() == OnComplete.DeleteApplication, Return(Int(0))    ],

        [Txn.on_completion() == OnComplete.UpdateApplication, Return(Int(1))    ],

        [Txn.on_completion() == OnComplete.CloseOut, Return(Int(0))             ],
        
        [Txn.on_completion() == OnComplete.OptIn, Return(Int(1))                ],

        [Txn.application_args[0] == Bytes("deposit"), deposit                   ],
    )

    return program


def clear_state_program():

    return Int(1)


with open("approval.teal", "w") as f:
    compiled = compileTeal(approval_program(), mode=Mode.Application, version=6)
    f.write(compiled)

with open("clear_state.teal", "w") as f:
    compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=6)
    f.write(compiled)



