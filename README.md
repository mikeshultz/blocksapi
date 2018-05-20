# blocks-api

RESTful API for unusual and uncommon blockchain queries.

## Install

    python setup.py install

## Usage

    blocksapi

## Docker Build & Deploy

    ./deploy.sh v0.0.1b3

## API

All API endpoints are prefixed by the version number.  For instance, a call to
`block` would be `/v1/block`.

All calls are limited to 100 returned objects.  You can paginate by using the 
request object parameter `page`.

### block

Query for groups of blocks.

#### Request Object

    {
        'block_number': 1,
        "start": 123,
        "end": 443920,
        "start_time": 1514592000,
        "end_time": 1514851140,
        "page": 1
    }

- `block_number`: A single block to retreive
- `start`: The beginning of a range of block numbers to retreive
- `end`: The end of a range of block numbers to retreive
- `start_time`: The unix timestamp for the start of a range of blocks to retreive
- `end_time`: The unix timestamp for the end of a range of blocks to retreive
- `has_transactions`: Whether or not the block has transactions
- `page`: The page number of results to retreive

#### Response

    {
        "page": 1,
        "results": [
            {
                "block_number": 1,
                "block_timestamp": 1514592000,
                "hash": "0x88e96d4537bea4d9c05d12549907b32561d3bf31f45aae734cdc119f13406cb6",
                "miner": "0x05a56E2D52c817161883f50c441c3228CFe54d9f",
                "nonce": 6024642674226568900,
                "difficulty": 17171480576,
                "gas_used": 0,
                "gas_limit": 5000,
                "size": 537
            }
        ]
    }

### transaction

Query for transactions.

#### Reqeust Object

    {
        "hash": "0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060",
        "block_number": 1,
        "from_address": "0xA1E4380A3B1f749673E270229993eE55F35663b4",
        "to_address": "0x5DF9B87991262F6BA471F09758CDE1c0FC1De734"
    }

#### Response

    {
        "page": 1,
        "results": [
            {
                "hash": "0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060",
                "block_number": 1,
                "from_address": "0xA1E4380A3B1f749673E270229993eE55F35663b4",
                "to_address": "0x5DF9B87991262F6BA471F09758CDE1c0FC1De734",
                "value": 31337,
                "gas_price": 50000000000000,
                "gas_limit": 21000,
                "nonce": 0,
                "input": "0x"
            }
        ]
    }