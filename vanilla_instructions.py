from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.system_program import create_account, CreateAccountParams
from spl.token.constants import MINT_LEN, TOKEN_PROGRAM_ID
from spl.token.instructions import initialize_mint, InitializeMintParams, \
    create_associated_token_account, get_associated_token_address, \
    mint_to, MintToParams, approve, ApproveParams

from utils import get_minimum_balance_rent_exemption, get_config_space

from constants import CANDY_MACHINE_PROGRAM_ID


async def get_create_new_config_account_instructions(async_client, new_account, from_account, num_nfts):
    space_needed = get_config_space(num_nfts)
    min_lamports = await get_minimum_balance_rent_exemption(async_client, space_needed)

    print("space needed for %s nfts: %s bytes" % (num_nfts, space_needed))
    print("minimum lamports for rent exemption for %s bytes : %s" % (space_needed, min_lamports))

    instruction = create_account(
        CreateAccountParams(
            from_pubkey=from_account.public_key,
            new_account_pubkey=new_account.public_key,
            lamports=min_lamports, space=space_needed, program_id=PublicKey(CANDY_MACHINE_PROGRAM_ID))
    )
    return ([instruction], [from_account, new_account])


async def get_user_account_mint_prep_instructions(async_client, user_account):
    mint_account = Keypair()
    instruction_list = []
    min_lamports = await get_minimum_balance_rent_exemption(async_client, MINT_LEN)

    create_account_instruction = create_account(
        CreateAccountParams(
            from_pubkey=user_account.public_key,
            new_account_pubkey=mint_account.public_key,
            lamports=min_lamports,
            space=MINT_LEN,
            program_id=TOKEN_PROGRAM_ID
        )
    )
    instruction_list.append(create_account_instruction)

    # no freeze rn bleh
    initialize_mint_instruction = initialize_mint(
        InitializeMintParams(
            decimals=0,
            program_id=TOKEN_PROGRAM_ID,
            mint=mint_account.public_key,
            mint_authority=user_account.public_key
        )
    )

    instruction_list.append(initialize_mint_instruction)

    create_assoc_instruction = create_associated_token_account(
        payer=user_account.public_key,
        owner=user_account.public_key,
        mint=mint_account.public_key
    )

    instruction_list.append(create_assoc_instruction)
    assoc_token_account = get_associated_token_address(user_account.public_key, mint_account.public_key)
    mint_to_instruction = mint_to(
        params=MintToParams(
            program_id=TOKEN_PROGRAM_ID,
            mint=mint_account.public_key,
            dest=assoc_token_account,
            mint_authority=user_account.public_key,
            amount=1
        )
    )

    instruction_list.append(mint_to_instruction)

    return (mint_account, instruction_list, [user_account, mint_account])

def get_approval_instruction(user_account, purchase_token, amount):
    transfer_authority_keypair = Keypair()
    assoc_token_account_public_key = get_associated_token_address(user_account.public_key,
                                                                  PublicKey(purchase_token))
    approval_instruction = approve(
        ApproveParams(
            program_id=TOKEN_PROGRAM_ID,
            source=assoc_token_account_public_key,
            delegate=transfer_authority_keypair.public_key,
            owner=user_account.public_key,
            amount=amount
        )
    )

    return (approval_instruction, transfer_authority_keypair)

