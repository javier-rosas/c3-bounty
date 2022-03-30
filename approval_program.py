# This example is provided for informational purposes only and has not been audited for security.

from pyteal import *


def approval_program():

 
    deposit = Return(Int(1))

    program = Cond(

        [Txn.application_id() == Int(0), Return(Int(1))                         ],

        [Txn.on_completion() == OnComplete.DeleteApplication, Return(Int(0))    ],

        [Txn.on_completion() == OnComplete.UpdateApplication, Return(Int(0))    ],

        [Txn.on_completion() == OnComplete.CloseOut, Return(Int(1))             ],
        
        [Txn.on_completion() == OnComplete.OptIn, Return(Int(1))                ],

        [Txn.application_args[0] == Bytes("deposit"), deposit                   ],
    )

    return program


def clear_state_program():

    return Int(1)


with open("vote_approval.teal", "w") as f:
    compiled = compileTeal(approval_program(), mode=Mode.Application, version=6)
    f.write(compiled)

with open("vote_clear_state.teal", "w") as f:
    compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=6)
    f.write(compiled)

    