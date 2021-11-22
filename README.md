# candypy
example code for interacting with solana anchor programs - candymachine

THIS IS PURELY SAMPLE CODE TO FORK, MODIFY, UNDERSTAND AND INTERACT WITH CANDYMACHINE USING ANCHORPY

I'll probably work on making this more resilient and fully featured, but at the moment, it mainly serves as an example for 
1. how to use anchorpy
2. to understand candymachine better.

the candymachine typescript client is amazing, but it couples together too many concerns - this is meant to interact with each instruction separately.

Interaction is primarily via command line arguments, rather than config files, to make it more explicit

# some information about candymachine
1. candymachine is an anchor program
2. while a large portion of interacting with it is via anchorpy, there are still a few places where the interactions are directly through solanapy - mostly using spl-token, spl-token-metadata

# accounts used
There are 2 main accounts used by candymachine
1. A config account which keeps track of total supply as well as rows [{ name: name, nft_metadata_uri: nft_metadata_uri}]
2. A candymachine account which keeps track of the price and the date to go live (this can be updated)

# steps involved 
creating a candy machine involves the following steps at a high level
1. creating the config account  - using the create_config_account option. This is not an anchor interaction, but a vanilla interaction with the system program
2. Initializating the config account (this is mainly allocating space for it based on the number of NFTs to be loaded, as well as paying rent) - using the initialize_config_account command (anchor)
3. add NFTs into the config account (load the names and metadata urls for each nft as a separate row) - add_config_lines (anchor)
4. create the main candymachine account (this is the second account). It will keep track of price, livedate, item count, treasury address which gets the payment
5. update the candymachine account (this is optional, in case you want to change the date of the mint or the price)
6. Mint. This is usually done through a browser client, but for illustration purposes the code also includes a mint command

# step 1 
install the necessary packages
`pip install -r requirements.txt`

also install the solana command line cli. 

# step 2 
configure solana cli for the devnet and get an airdrop of 5-10 sol
`solana-keygen -o myfolder/wallet.json`

`solana config set -u d`

`solana airdrop 5 myfolder/wallet.json`

run the last command a few times in case it fails.
the key you just generted will serve the the payment key for configuring candymachine

# step 3
create the config account

`python main.py create_config_account myfolder/wallet.json 10`

2yeCtaKgESShtnDWdH24EuhZLrfnkVoHk9t3WmmnJcaf

Note down the config accounts public address since you'll be using it for other commands 

couple of things of note here-
1. the space needed is calculated based on number of NFTs
2. the rent exemption amount is in turn calculated by amount of space necesarry/ This can be optimized for a short term rent to make it easier, but i'm lazy for now
3. the config accounts ownership is passed onto the CANDY_MACHINE_PROGRAM_ID

# step 4
initialize the config account - store some basic data in it - authority, number of nfts, royalties, royalty split between creators

`python main.py initialize_config_account  myfolder/wallet.json ROBOTEST 10 2yeCtaKgESShtnDWdH24EuhZLrfnkVoHk9t3WmmnJcaf 100`

here - 
1. ROBOTEST is the symbol
2. royalties are basis points (1/100 * percentage)
3. creator array which is an option json (do a -h to check it out) which has a % split of which address gets what % of the royalty. This should total to 100 and candymachine ts check for this but thats not the point of this tutorial for now.


# step 5
Add config lines, i.e. the actual NFTs you're going to load into the machine

`python main.py add_config_lines myfolder/wallet.json 2yeCtaKgESShtnDWdH24EuhZLrfnkVoHk9t3WmmnJcaf sample_files\nft_rows.json`

These config lines are in the sample_files folder and the formation structure is a list of dicts-
```
[
  {"name": "rob #1",
 "uri": "https://gateway.pinata.cloud/ipfs/QmaPtzAKea1fcuaMhukiPsTVBEH7wwmMhDTxaN5Jz2zQq9/1.json"},
  {"name": "rob #2",
   "uri": "https://gateway.pinata.cloud/ipfs/QmaPtzAKea1fcuaMhukiPsTVBEH7wwmMhDTxaN5Jz2zQq9/2.json"},
  {"name": "rob #3",
   "uri": "https://gateway.pinata.cloud/ipfs/QmaPtzAKea1fcuaMhukiPsTVBEH7wwmMhDTxaN5Jz2zQq9/3.json"},
  {"name": "rob #4",
   "uri": "https://gateway.pinata.cloud/ipfs/QmaPtzAKea1fcuaMhukiPsTVBEH7wwmMhDTxaN5Jz2zQq9/4.json"},
  {"name": "rob #5",
   "uri": "https://gateway.pinata.cloud/ipfs/QmaPtzAKea1fcuaMhukiPsTVBEH7wwmMhDTxaN5Jz2zQq9/5.json"}
]
```
This sample has only 5 NFTs. It's possible to edit the code and upload the NFTs in batches, but since this is primarily for learning purposes, I'm keeping it simple (hardcoded index). becuase the index is always 0, it'll overwrite with the new set of files in the sample_files folder.
Also, you'll notice this has the uri's already. Yes. This code expects you have your NFT uploaded to arweave or ipfs first. Another reason I went down this route besides learning was to keep a clear separation between code interating with solana and code interacting with arweave, file storage

# step 6
create the actual cnady machine account

`python main.py initialize_candy_machine  myfolder/wallet.json 0.5 now 10 2yeCtaKgESShtnDWdH24EuhZLrfnkVoHk9t3WmmnJcaf ANAwyQU9HCZXaKkypAHkvTGzDEDGvVsHxto7jLhenp7q`

"now" is s convenience ooption, but you want to pass the epoch timestamp of when you want the machine to go live
2yeCtaKgESShtnDWdH24EuhZLrfnkVoHk9t3WmmnJcaf as you know is the config account address
ANAwyQU9HCZXaKkypAHkvTGzDEDGvVsHxto7jLhenp7q in this case is the wallet that should hold treasury funds

# step 7
candy machine can be optionally updated. as many times as you like. Its mainly the price and the live date
`python main.py update_candy_machine myfolder/wallet.json 0.33 now 2yeCtaKgESShtnDWdH24EuhZLrfnkVoHk9t3WmmnJcaf`
- price
- time (epoch)
- config address

#step 8
This is actually the most complex part. Here is what's happening when you're minting an NFT
## NON ANCHOR INSTRUCTIONS
0. IMPORTANT: this is from a client side, so you would preferably want to configure another wallet + airdrop some sol in it.
1. you create a new NFT token
2. you create an associated token account derived from your main address to "hold" the NFT
3. you allocate some default mint space for the account (based on some constants) - rent exempt amount because these need to be permanent
4. you add approval for the candymachine to transfer the NFT out of your wallet, modify it and return the NFT token (now with metadata populated

## Anchor instructions
1. The anchor mint command doesn't take any args and just takes a list of accounts and signatures

`python main.py mint myfolder/client-wallet.json 2yeCtaKgESShtnDWdH24EuhZLrfnkVoHk9t3WmmnJcaf ANAwyQU9HCZXaKkypAHkvTGzDEDGvVsHxto7jLhenp7q NAwyQU9HCZXaKkypAHkvTGzDEDGvVsHxto7jLhenp7q`

myfolder/client-wallet.json is the new wallet creator for client side
config address - same old, 2yeCtaKgESShtnDWdH24EuhZLrfnkVoHk9t3WmmnJcaf
ANAwyQU9HCZXaKkypAHkvTGzDEDGvVsHxto7jLhenp7q - treasury address
ANAwyQU9HCZXaKkypAHkvTGzDEDGvVsHxto7jLhenp7q - authority


# step 8
once this is done, you can simply check the balance of your account
`spl-token accounts --owner`
Token                                         Balance
---------------------------------------------------------------
3W5RhXSBs5zyRpqeGUrC4xrN3ppNnRdBeYDYU3X1bhrp  1


