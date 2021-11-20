# _IdlInstruction(
#     name="mint_nft",
#     accounts=[
#         _IdlAccount(name="config", is_mut=False, is_signer=False),
#         _IdlAccount(name="candy_machine", is_mut=True, is_signer=False),
#         _IdlAccount(name="payer", is_mut=True, is_signer=True),
#         _IdlAccount(name="wallet", is_mut=True, is_signer=False),
#         _IdlAccount(name="metadata", is_mut=True, is_signer=False),
#         _IdlAccount(name="mint", is_mut=True, is_signer=False),
#         _IdlAccount(name="mint_authority", is_mut=False, is_signer=True),
#         _IdlAccount(name="update_authority", is_mut=False, is_signer=True),
#         _IdlAccount(name="master_edition", is_mut=True, is_signer=False),
#         _IdlAccount(name="token_metadata_program", is_mut=False, is_signer=False),
#         _IdlAccount(name="token_program", is_mut=False, is_signer=False),
#         _IdlAccount(name="system_program", is_mut=False, is_signer=False),
#         _IdlAccount(name="rent", is_mut=False, is_signer=False),
#         _IdlAccount(name="clock", is_mut=False, is_signer=False),
#     ],
#     args=[],
# )

from anchorpy import Provider, Program, Context, Wallet
from solana.publickey import PublicKey
from solana.sysvar import SYSVAR_CLOCK_PUBKEY
from spl.token.constants import TOKEN_PROGRAM_ID

from constants import CANDY_MACHINE_PROGRAM_ID, METADATA_PROGRAM_ID, SYSTEM_PROGRAM_ID, SYSVAR_RENT_PUBKEY
from pda import get_metadata_account, get_candy_machine_pda_nonce, get_master_edition


async def mint_one_nft(async_client, user_key, config_pub_key_string, mint_key, treasury_key_str, instructions):
    provider = Provider(async_client, Wallet(payer=user_key))

    idl = await Program.fetch_idl(CANDY_MACHINE_PROGRAM_ID, provider)

    candyprog = Program(idl=idl, program_id=CANDY_MACHINE_PROGRAM_ID, provider=provider)
    metadata = get_metadata_account(mint_key.public_key)

    candy_machine_pda, _ = get_candy_machine_pda_nonce(config_pub_key_string)
    master_edition = get_master_edition(mint_key.public_key)

    result = await candyprog.rpc["mint_nft"](
        ctx=Context(
            accounts={
                "config": PublicKey(config_pub_key_string),
                "candy_machine":candy_machine_pda,
                "payer": user_key.public_key,
                "wallet": PublicKey(treasury_key_str),
                "metadata":metadata,
                "mint":mint_key.public_key,
                "mint_authority":user_key.public_key,
                "update_authority":user_key.public_key,
                "master_edition":master_edition,
                "token_metadata_program": PublicKey(METADATA_PROGRAM_ID),
                "token_program": TOKEN_PROGRAM_ID,
                "system_program": PublicKey(SYSTEM_PROGRAM_ID),
                "rent": PublicKey(SYSVAR_RENT_PUBKEY),
                "clock": PublicKey(SYSVAR_CLOCK_PUBKEY),
            },
            pre_instructions=instructions,
            signers=[user_key, mint_key]
        )
    )
    return result