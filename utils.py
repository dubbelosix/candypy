import json
import math

from jsonschema import validate

from solana.keypair import Keypair
from constants import CONFIG_ARRAY_START, CONFIG_LINE_SIZE


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_keypair(keypath):
    with open(keypath) as f:
        kpb = json.loads(f.read())
    return Keypair.from_secret_key(secret_key=bytes(kpb))


def get_config_space(num_lines):
    return CONFIG_ARRAY_START + 4 + num_lines * CONFIG_LINE_SIZE + 4 + math.ceil(num_lines / 8.0)


async def get_minimum_balance_rent_exemption(client, account_size):
    resp = await client.get_minimum_balance_for_rent_exemption(account_size)
    exemption_lamports = int(resp["result"])
    return exemption_lamports

def get_default_creator_array(payment_key):
    return [
        {
            "address": payment_key.public_key,
            "verified": False,
            "share": 100
        }
    ]

def get_creator_array(json_file):
    creator_array_json_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "address": {"type": "string"},
                    "verified": {"type": "boolean"},
                    "share": {"type": "integer"}
                },
                "required": ["address", "verified", "share"]
            }
        }

    with open(json_file) as f:
        json_contents = json.loads(f.read())
    validate(instance=json_contents, schema=creator_array_json_schema)
    return json_contents

def get_nft_rows(json_file):
    nft_array_json_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "uri": {"type": "string"}
                },
                "required": ["name", "uri"]
            }
        }

    with open(json_file) as f:
        json_contents = json.loads(f.read())
    validate(instance=json_contents, schema=nft_array_json_schema)
    return json_contents
