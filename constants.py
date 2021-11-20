# This is from the typescript client
# export const CONFIG_ARRAY_START =
#   32 + // authority
#   4 +
#   6 + // uuid + u32 len
#   4 +
#   10 + // u32 len + symbol
#   2 + // seller fee basis points
#   1 +
#   4 +
#   5 * 34 + // optional + u32 len + actual vec
#   8 + //max supply
#   1 + //is mutable
#   1 + // retain authority
#   4; // max number of lines;
CONFIG_ARRAY_START = 247
CONFIG_LINE_SIZE = 4 + 32 + 4 + 200

CHUNK_SIZE = 1000
SELLER_BASIS_DEFAULT = 100

TESTNET = "https://api.testnet.solana.com"
MAINNET = "https://api.mainnet-beta.solana.com"
DEVNET = "https://api.devnet.solana.com"
CANDY_MACHINE_PROGRAM_ID = "cndyAnrLdpjq1Ssp1z8xxDsB8dxe7u4HL5Nxi2K5WXZ"

METADATA_PROGRAM_ID = 'metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s'
SYSTEM_PROGRAM_ID = '11111111111111111111111111111111'
SYSVAR_RENT_PUBKEY = 'SysvarRent111111111111111111111111111111111'
ASSOCIATED_TOKEN_ACCOUNT_PROGRAM_ID = 'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL'
