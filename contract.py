from pyteal import *


def approval_program():

    @Subroutine(TealType.none)
    def global_safety_checks():
        return Seq([
            # assert only one transaction in the group 
            Assert( Global.group_size() == Int(1)                                   ),
            # assert the receiver of the transaction is the smart contract address
            Assert( Txn.receiver() == Global.current_application_address()          ),
            # assert there is only one argument: "deposit", "asset_id", "amount"
            Assert( Txn.application_args.length() == Int(3)                         ),
            # assert the accounts array is of size 1 (only the account sending the transaction)
            Assert( Txn.accounts.length() == Int(1)                                 ),
            # assert the applications array is of size 1 (only the smart contract we are making the transaction to)
            Assert( Txn.applications.length() == Int(1)                             ),
            # assert the array of assets is of size 1 
            Assert( Txn.assets.length() == Int(1)                                   ),
            # assert the asset close to is the global zero address
            Assert( Txn.asset_close_to() == Global.zero_address()                   ),
            # assert the algos close_remainer_to is the global zero address 
            Assert( Txn.close_remainder_to() == Global.zero_address()               ),

            Return()
        ])


    '''
    Argument: asa id (uint64)
    Returns: None 

    Function makes an inner transaction that opts the smart contract to the ASA provided
    '''
    @Subroutine(TealType.none)
    def smart_contract_opt_in_to_asa(asa_id):
     
        return Seq([
        
        InnerTxnBuilder.Begin(),

            InnerTxnBuilder.SetFields({
            TxnField.type_enum : TxnType.AssetTransfer,
            TxnField.xfer_asset : asa_id,
            TxnField.asset_amount : Int(0),
            TxnField.asset_sender : Global.current_application_address(),
            TxnField.asset_receiver: Global.current_application_address(),
            TxnField.asset_close_to : Global.zero_address(),

            }),

        InnerTxnBuilder.Submit()
            
        ])


    @Subroutine(TealType.none)
    def inner_transaction_with_rekey(asa_id):

        
        smart_contract_asset_balance = AssetHolding.balance( Global.current_application_address(), asa_id ) 

        # if smart contract is not opted in to the asset, call smart_contract_opt_in_to_asa()
        return Seq([
        # ~smart_contract_asset_balance.hasValue() returns Int(1) if the smart contract is not opted in to asset
        If( ~smart_contract_asset_balance.hasValue() ).
            Then(
                # if smart contract is not opted in to the asset, send an opt in transaction for the asset 
                smart_contract_opt_in_to_asa(asa_id)
            )
        ])

        
    deposit = Seq([
        global_safety_checks(),
        #inner_transaction_with_rekey(),
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



