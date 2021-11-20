# _IdlInstruction(
#     name="initialize_candy_machine",
#     accounts=[
#         _IdlAccount(name="candy_machine", is_mut=True, is_signer=False),
#         _IdlAccount(name="wallet", is_mut=False, is_signer=False),
#         _IdlAccount(name="config", is_mut=False, is_signer=False),
#         _IdlAccount(name="authority", is_mut=False, is_signer=True),
#         _IdlAccount(name="payer", is_mut=True, is_signer=True),
#         _IdlAccount(name="system_program", is_mut=False, is_signer=False),
#         _IdlAccount(name="rent", is_mut=False, is_signer=False),
#     ],
#     args=[
#         _IdlField(name="bump", type="u8"),
#         _IdlField(name="data", type=_IdlTypeDefined(defined="CandyMachineData")),
#     ],
# )

# _IdlTypeDef(
#     name="CandyMachineData",
#     type=_IdlTypeDefTyStruct(
#         fields=[
#             _IdlField(name="uuid", type="string"),
#             _IdlField(name="price", type="u64"),
#             _IdlField(name="items_available", type="u64"),
#             _IdlField(name="go_live_date", type=_IdlTypeOption(option="i64")),
#         ],
#         kind="struct",
#     ),
# )
from anchorpy import Provider, Wallet, Program, Context
from solana.publickey import PublicKey

from constants import CANDY_MACHINE_PROGRAM_ID, SYSTEM_PROGRAM_ID, SYSVAR_RENT_PUBKEY
from pda import get_candy_machine_pda_nonce


async def initialize_candy_machine(async_client, main_key, config_pub_key_str, treasury_pub_key_str,
                                   candy_machine_pda, bump, livedate, price, item_count):
    provider = Provider(async_client, Wallet(payer=main_key))
    idl = await Program.fetch_idl(CANDY_MACHINE_PROGRAM_ID, provider)
    candyprog = Program(idl=idl, program_id=CANDY_MACHINE_PROGRAM_ID, provider=provider)
    # uuid has to be 6 characters in length
    cmuuid = config_pub_key_str[:6]
    result = await candyprog.rpc["initialize_candy_machine"](
        bump,
        {
            "uuid": cmuuid,
            "price": price,
            "items_available": item_count,
            "go_live_date": livedate
        },
        ctx=Context(
            accounts={
                "candy_machine": PublicKey(candy_machine_pda),
                "wallet": PublicKey(treasury_pub_key_str),
                "config": PublicKey(config_pub_key_str),
                "authority": main_key.public_key,
                "payer": main_key.public_key,
                "system_program": PublicKey(SYSTEM_PROGRAM_ID),
                "rent": PublicKey(SYSVAR_RENT_PUBKEY)
            },
            signers=[main_key]
        )
    )
    return result