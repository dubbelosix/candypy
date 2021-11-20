import os
import asyncio
import argparse
import math
import time

from solana.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction

from anchor_commands.initialize_candy_machine import initialize_candy_machine
from anchor_commands.mint_nft import mint_one_nft
from anchor_commands.update_candy_machine import update_candy_machine
from pda import get_candy_machine_pda_nonce
from vanilla_instructions import get_create_new_config_account_instructions, get_user_account_mint_prep_instructions, \
    get_approval_instruction
from anchor_commands.add_config_lines import add_nfts_to_machine
from anchor_commands.initialize_config import initialize_candymachine_for_config_account

from constants import DEVNET, TESTNET, MAINNET
from utils import get_keypair, get_default_creator_array, get_creator_array, get_nft_rows

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def run_instructions(async_client, instruction_list, signature_list):
    tx = Transaction()
    for i in instruction_list:
        tx = tx.add(i)
    response = await async_client.send_transaction(tx, *signature_list)
    return response


async def main():

    parser = argparse.ArgumentParser(description='candy machine configurations')
    parser.add_argument('--usenet', action="store", choices=["devnet", "testnet", "mainnet"],
                        help='path to the keypair used for payments')
    parser.add_argument('--customnet', action="store",
                        help='custom rpc endpoint to hit')

    subparsers = parser.add_subparsers(dest="subcommand_name", help='candy machine config help')

    parser_config_creator = subparsers.add_parser('create_config_account', help='create account to store NFTs')
    parser_config_creator.add_argument('payment_key', action="store", help='path to the keypair used for payments')
    parser_config_creator.add_argument('num_nfts', action="store",
                                       help='number of nfts this config will hold. determines space')

    parser_init_config = subparsers.add_parser('initialize_config_account',
                                               help='initialize the config account in candymachine. allocate space')
    parser_init_config.add_argument('payment_key', action="store", help='path to the keypair used for payments')
    parser_init_config.add_argument('nft_symbol', action="store", help='NFT symbol')
    parser_init_config.add_argument('num_nfts', action="store", help='number of nfts')
    parser_init_config.add_argument('config_pub_key', action="store", help='public key of config account')
    parser_init_config.add_argument('seller_basis_points', action="store", help='basis points / royalty')
    parser_init_config.add_argument('--is_immutable', action="store_true", help='mutability')
    parser_init_config.add_argument('--creator_json_file', action="store",
                                    help='optional json list of creators. Users the payment_key by default')

    parser_init_addlines = subparsers.add_parser('add_config_lines',
                                                 help='initialize the config account in candymachine. allocate space')
    parser_init_addlines.add_argument('payment_key', action="store", help='path to the keypair used for payments')
    parser_init_addlines.add_argument('config_pub_key', action="store", help='public key of config account')
    parser_init_addlines.add_argument('name_uri_json', action="store", help='file containing names mapped to metadata '
                                                                            'uris')

    parser_create_machine = subparsers.add_parser('initialize_candy_machine',
                                                  help='create the main candy machine account')
    parser_create_machine.add_argument('payment_key', action="store", help='path to the keypair used for payments')
    parser_create_machine.add_argument('price', action="store", help='price per NFT in sol')
    parser_create_machine.add_argument('livedate', action="store", help='date when the mint should be live epoch time')
    parser_create_machine.add_argument('itemcount', action="store", help='number of nfts for the candymachine')
    parser_create_machine.add_argument('config_pub_key', action="store", help='public key of config account')
    parser_create_machine.add_argument('treasury_pub_key', action="store", help='public key of treasury account')

    parser_update_machine = subparsers.add_parser('update_candy_machine',
                                                  help='update the price and date in the candy machine')
    parser_update_machine.add_argument('payment_key', action="store", help='path to the keypair used for payments')
    parser_update_machine.add_argument('price', action="store", help='price per NFT in sol')
    parser_update_machine.add_argument('livedate', action="store", help='date when the mint should be live epoch time')
    parser_update_machine.add_argument('config_pub_key', action="store", help='public key of config account')

    parser_mint = subparsers.add_parser('mint',
                                        help='mint from a machine')
    parser_mint.add_argument('payment_key', action="store", help='path to the keypair used for payments')
    parser_mint.add_argument('config_pub_key', action="store", help='public key of config account')
    parser_mint.add_argument('treasury_pub_key', action="store", help='wallet pub key')
    parser_mint.add_argument('mint_auth', action="store", help='wallet pub key')

    args = parser.parse_args()

    use_network = DEVNET
    if args.usenet == "testnet":
        use_network = TESTNET
    elif args.usenet == "mainnet":
        use_network = MAINNET

    payment_keypair = get_keypair(args.payment_key)

    # vanilla
    if args.subcommand_name == "create_config_account":
        new_account_keypair = Keypair()
        num_nfts = int(args.num_nfts)
        async_client = AsyncClient(endpoint=use_network)
        from_account_keypair = payment_keypair
        (instruction_list, signature_list) = await get_create_new_config_account_instructions(async_client,
                                                                                              new_account_keypair,
                                                                                              from_account_keypair,
                                                                                              num_nfts)
        response = await run_instructions(async_client, instruction_list, signature_list)
        print(response)
        print("new config account generated with candymachine as owner: %s" % new_account_keypair.public_key)


    # anchor
    elif args.subcommand_name == "initialize_config_account":
        num_nfts = int(args.num_nfts)
        config_pub_key = args.config_pub_key
        nft_symbol = args.nft_symbol
        seller_basis_points = int(args.seller_basis_points)
        is_mut = True
        if args.is_immutable:
            is_mut = False

        if not args.creator_json_file:
            creator_array = get_default_creator_array(payment_keypair)
        else:
            creator_array = get_creator_array(args.creator_json_file)

        async_client = AsyncClient(endpoint=use_network)

        response = await initialize_candymachine_for_config_account(async_client,
                                                                    payment_keypair,
                                                                    config_pub_key,
                                                                    num_nfts,
                                                                    nft_symbol,
                                                                    seller_basis_points,
                                                                    is_mut,
                                                                    num_nfts,
                                                                    creator_array)
        print(response)

    # anchor
    elif args.subcommand_name == "add_config_lines":
        config_pub_key_str = args.config_pub_key
        nft_rows_json_file = args.name_uri_json
        nft_rows = get_nft_rows(nft_rows_json_file)
        async_client = AsyncClient(endpoint=use_network)
        response = await add_nfts_to_machine(async_client, payment_keypair, config_pub_key_str, nft_rows)
        print(response)

    # anchor
    elif args.subcommand_name == "initialize_candy_machine":
        async_client = AsyncClient(endpoint=use_network)
        price = math.ceil(float(args.price) * 1000000000)
        config_pub_key_str = args.config_pub_key
        itemcount = int(args.itemcount)
        treasury_pub_key_str = args.treasury_pub_key
        if args.livedate == "now":
            livedate = int(time.time())
        else:
            livedate = int(args.livedate)
        candy_machine_pda, bump = get_candy_machine_pda_nonce(config_pub_key_str)
        response = await initialize_candy_machine(async_client,
                                                  payment_keypair,
                                                  config_pub_key_str,
                                                  treasury_pub_key_str,
                                                  candy_machine_pda,
                                                  bump,
                                                  livedate,
                                                  price,
                                                  itemcount
                                                  )
        print("created candy machine with address: %s" % (candy_machine_pda.to_base58().encode()))
        print(response)

    # anchor
    elif args.subcommand_name == "update_candy_machine":
        async_client = AsyncClient(endpoint=use_network)
        price = math.ceil(float(args.price) * 1000000000)
        config_pub_key_str = args.config_pub_key
        candy_machine_pda, _ = get_candy_machine_pda_nonce(config_pub_key_str)
        if args.livedate == "now":
            livedate = int(time.time())
        else:
            livedate = int(args.livedate)

        result = await update_candy_machine(async_client,
                             payment_keypair,
                             candy_machine_pda,
                             price,
                             livedate)
        print(result)

    elif args.subcommand_name == "mint":
        async_client = AsyncClient(endpoint=use_network)
        config_pub_key_str = args.config_pub_key
        treasury_pub_key_str = args.treasury_pub_key
        mint_account, account_create_instructions, signers = await get_user_account_mint_prep_instructions(async_client,
                                                                                                           payment_keypair)
        approval_instruction, signers = get_approval_instruction(payment_keypair,
                                                          mint_account.public_key, 1)

        result = await mint_one_nft(async_client, payment_keypair, config_pub_key_str,
                           mint_account, treasury_pub_key_str, account_create_instructions + approval_instruction)
        print(result)


asyncio.run(main())
