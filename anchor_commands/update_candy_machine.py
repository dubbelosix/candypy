# _IdlInstruction(
#     name="update_candy_machine",
#     accounts=[
#         _IdlAccount(name="candy_machine", is_mut=True, is_signer=False),
#         _IdlAccount(name="authority", is_mut=False, is_signer=True),
#     ],
#     args=[
#         _IdlField(name="price", type=_IdlTypeOption(option="u64")),
#         _IdlField(name="go_live_date", type=_IdlTypeOption(option="i64")),
#     ],
# )

from anchorpy import Provider, Wallet, Program, Context
from solana.publickey import PublicKey

from constants import CANDY_MACHINE_PROGRAM_ID

async def update_candy_machine(async_client, main_key, candy_machine_pda, price, livedate):
    provider = Provider(async_client, Wallet(payer=main_key))

    idl = await Program.fetch_idl(CANDY_MACHINE_PROGRAM_ID, provider)
    candyprog = Program(idl=idl, program_id=CANDY_MACHINE_PROGRAM_ID, provider=provider)

    result = await candyprog.rpc["update_candy_machine"](
        price,
        livedate,
        ctx=Context(
            accounts={
                "candy_machine": PublicKey(candy_machine_pda),
                "authority": main_key.public_key,
            },
            signers=[main_key]
        )
    )
    return result