from solana.publickey import PublicKey

from constants import CANDY_MACHINE_PROGRAM_ID, METADATA_PROGRAM_ID


def get_candy_machine_pda_nonce(config_pub_key_str):
    uuid = config_pub_key_str[:6]
    result = PublicKey.find_program_address(
        [b'candy_machine', bytes(PublicKey(config_pub_key_str)), uuid.encode()],
        PublicKey(CANDY_MACHINE_PROGRAM_ID)
    )
    # 0 is the address
    # 1 is the nonce
    return (result[0], result[1])

def get_metadata_account(mint_key_str):
    return PublicKey.find_program_address(
        [b'metadata', bytes(PublicKey(METADATA_PROGRAM_ID)), bytes(PublicKey(mint_key_str))],
        PublicKey(METADATA_PROGRAM_ID)
    )[0]

def get_master_edition(mint_key_str):
    return PublicKey.find_program_address(
        [b'metadata', bytes(PublicKey(METADATA_PROGRAM_ID)), bytes(PublicKey(mint_key_str)), b"edition"],
        PublicKey(METADATA_PROGRAM_ID)
    )[0]
