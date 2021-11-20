# _IdlInstruction(
#     name="add_config_lines",
#     accounts=[
#         _IdlAccount(name="config", is_mut=True, is_signer=False),
#         _IdlAccount(name="authority", is_mut=False, is_signer=True),
#     ],
#     args=[
#         _IdlField(name="index", type="u32"),
#         _IdlField(
#             name="config_lines",
#             type=_IdlTypeVec(vec=_IdlTypeDefined(defined="ConfigLine")),
#         ),
#     ],
# )

# _IdlTypeDef(
#     name="ConfigLine",
#     type=_IdlTypeDefTyStruct(
#         fields=[
#             _IdlField(name="name", type="string"),
#             _IdlField(name="uri", type="string"),
#         ],
#         kind="struct",
#     ),
# )

from anchorpy import Provider, Wallet, Program, Context
from solana.publickey import PublicKey

from constants import CANDY_MACHINE_PROGRAM_ID,  CHUNK_SIZE
from utils import divide_chunks


async def add_nfts_to_machine(async_client,
                              main_key,
                              config_pub_key_str,
                              nft_items):
    provider = Provider(async_client, Wallet(payer=main_key))

    idl = await Program.fetch_idl(CANDY_MACHINE_PROGRAM_ID, provider)
    candyprog = Program(idl=idl, program_id=CANDY_MACHINE_PROGRAM_ID, provider=provider)
    idx = 0
    for chunked_list in divide_chunks(nft_items, CHUNK_SIZE):
        result = await candyprog.rpc["add_config_lines"](idx,
                                                       chunked_list,
                                                       ctx=Context(
                                                           accounts={
                                                               "config": PublicKey(config_pub_key_str),
                                                               "authority": main_key.public_key,
                                                           },
                                                           signers=[main_key]
                                                       )
                                                       )
        idx = len(chunked_list)
        print(result)