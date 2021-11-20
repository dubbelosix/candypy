# _IdlInstruction(
#     name="initialize_config",
#     accounts=[
#         _IdlAccount(name="config", is_mut=True, is_signer=False),
#         _IdlAccount(name="authority", is_mut=False, is_signer=False),
#         _IdlAccount(name="payer", is_mut=True, is_signer=True),
#         _IdlAccount(name="rent", is_mut=False, is_signer=False),
#     ],
#     args=[_IdlField(name="data", type=_IdlTypeDefined(defined="ConfigData"))],
# )


# _IdlTypeDef(
#     name="ConfigData",
#     type=_IdlTypeDefTyStruct(
#         fields=[
#             _IdlField(name="uuid", type="string"),
#             _IdlField(name="symbol", type="string"),
#             _IdlField(name="seller_fee_basis_points", type="u16"),
#             _IdlField(
#                 name="creators",
#                 type=_IdlTypeVec(vec=_IdlTypeDefined(defined="Creator")),
#             ),
#             _IdlField(name="max_supply", type="u64"),
#             _IdlField(name="is_mutable", type="bool"),
#             _IdlField(name="retain_authority", type="bool"),
#             _IdlField(name="max_number_of_lines", type="u32"),
#         ],
#         kind="struct",
#     ),
# )

from anchorpy import Provider, Wallet, Program, Context
from solana.publickey import PublicKey

from constants import CANDY_MACHINE_PROGRAM_ID, SYSVAR_RENT_PUBKEY


async def initialize_candymachine_for_config_account(
        async_client,
        main_key,
        config_pubkey,
        num_lines,
        nft_symbol,
        seller_basis,
        is_mut,
        max_supply,
        creator_array):
    provider = Provider(async_client, Wallet(payer=main_key))

    idl = await Program.fetch_idl(PublicKey(CANDY_MACHINE_PROGRAM_ID), provider)

    # uuid has to be 6 characters in length
    cmuuid = config_pubkey[:6]
    candyprog = Program(idl=idl, program_id=CANDY_MACHINE_PROGRAM_ID, provider=provider)

    result = await candyprog.rpc["initialize_config"]({
        "uuid": cmuuid,
        "max_number_of_lines": num_lines,
        "symbol": nft_symbol,
        "seller_fee_basis_points": seller_basis,
        "is_mutable": is_mut,
        "max_supply": max_supply,
        "retain_authority": True,
        "creators": creator_array
    },
        ctx=Context(
            accounts={
                "config": PublicKey(config_pubkey),
                "authority": main_key.public_key,
                "payer": main_key.public_key,
                "rent": PublicKey(SYSVAR_RENT_PUBKEY),
            },
            signers=[main_key]
        )
    )
    return result
