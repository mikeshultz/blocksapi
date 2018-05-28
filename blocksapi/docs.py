JSON_SCHEMA = [
    {
        "uri": "/",
        "method": "GET",
        "description": "Describe the available API endpoints",
        "request": None,
        "response": {
            "title": "Response",
            "type": "object",
            "properties": {
                "endpoints": {
                    "type": "array",
                    "description": "An array of endpoints in JSON-Schema",
                    "items": {
                        "type": "object",
                        "properties": {
                            "$endpoint_uri": {
                                "type": "object",
                                "properties": {
                                    "method": {
                                        "type": "string",
                                        "description": "The HTTP method used to make the request."
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "A description of the endpoint."
                                    },
                                    "request": {
                                        "type": "object",
                                        "description": "The JSON request body, if any."
                                    },
                                    "response": {
                                        "type": "object",
                                        "description": "The JSON response of the endpoint."
                                    }
                                },
                                "required": ["method", "description", "reesponse"]
                            } 
                        },
                        "required": []
                    }
                }
            },
            "required": ["endpoints"]
        }
    },
    {
        "uri": "/health",
        "method": "GET",
        "description": "Show the current state of the API",
        "request": None,
        "response": {
            "title": "Response",
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "A description of the health of the API.  Good: 'ok'"
                },
                "block_number": {
                    "type": "integer",
                    "description": "The current max block the API knows about."
                }
            },
            "required": ["message", "block_number"]
        }
    },
    {
        "uri": "/block",
        "method": "POST",
        "description": "Query for blocks",
        "request": {
            "title": "Request",
            "type": "object",
            "properties": {
                "block_number": {
                    "type": "number"
                },
                "start": {
                    "type": "number",
                    "description": "The starting block number of the range"
                },
                "end": {
                    "type": "number",
                    "description": "The ending block number of the range. (Required when start is provided)",
                },
                "start_time": {
                    "format": "date-time",
                    "type": "string",
                    "description": "The start date time of the range"
                },
                "end_time": {
                    "format": "date-time",
                    "type": "string",
                    "description": "The ending date time of the range. (Required when start_time is provided)",
                }
            },
            "required": []
        },
        "response": {
            "title": "Response",
            "type": "object",
            "properties": {
                "page": {
                    "type": "number"
                },
                "pages": {
                    "type": "number",
                },
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "block_number": {
                                "type": "number"
                            },
                            "block_timestamp": {
                                "format": "date-time",
                                "type": "string",
                                "description": "A UTC ISO format timestamp"
                            },
                            "hash": {
                                "type": "string",
                                "description": "The block hash as a hex string"
                            },
                            "miner": {
                                "type": "string",
                                "description": "The address of the account that mined this block"
                            },
                            "nonce": {
                                "type": "number",
                                "description": "The block nonce"
                            },
                            "difficulty": {
                                "type": "number",
                                "description": "The difficulty the block was mined at"
                            },
                            "gas_used": {
                                "type": "number",
                                "description": "The total gas used for the block"
                            },
                            "gas_limit": {
                                "type": "number",
                                "description": "The gas limit for the block"
                            }, 
                            "size": {
                                "type": "number",
                                "description": "The size of the block"
                            }
                        },
                        "required": [
                            "block_number",
                            "block_timestamp",
                            "hash",
                            "miner",
                            "nonce",
                            "difficulty",
                            "gas_used",
                            "gas_limit",
                            "size"
                        ]
                    }
                }
            },
            "required": ["page", "pages", "result"]
        }
    },
    {
        "uri": "/transaction",
        "method": "POST",
        "description": "Query for transactions",
        "request": {
            "title": "Request",
            "type": "object",
            "properties": {
                "block_number": {
                    "type": "number",
                    "description": "The block the tx was mined in."
                },
                "hash": {
                    "type": "string",
                    "description": "The transaction hash."
                },
                "from_address": {
                    "type": "string",
                    "description": "The address the transaction was sent from."
                },
                "to_address": {
                    "type": "string",
                    "description": "The address the transaction was sent to.",
                },
                "address": {
                    "type": "string",
                    "description": "The address the transaction was sent from or to."
                }
            },
            "required": []
        },
        "response": {
            "title": "Response",
            "type": "object",
            "properties": {
                "page": {
                    "type": "number",
                    "description": "The page number currently being served."
                },
                "pages": {
                    "type": "number",
                    "description": "The total pages available."
                },
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "hash": {
                                "type": "string",
                                "description": "The sha3 hash of the transaction."
                            },
                            "block_number": {
                                "type": "number",
                                "description": "The block the tx was mined in."
                            },
                            "from_address": {
                                "type": "string",
                                "description": "The address of the acount that signed the tx."
                            },
                            "to_address": {
                                "type": "string",
                                "description": "The destination account or contract for the tx."
                            },
                            "value": {
                                "type": "number",
                                "description": "The amount of wei sent."
                            },
                            "gas_price": {
                                "type": "number",
                                "description": "The gas price in wei."
                            },
                            "gas_limit": {
                                "type": "number",
                                "description": "The gas limit for the transaction."
                            },
                            "nonce": {
                                "type": "number",
                                "description": "The nonce for the transaction."
                            },
                            "input": {
                                "type": "string",
                                "description": "The input data for the tx."
                            }
                        },
                        "required": [
                            "hash",
                            "block_number",
                            "from_address",
                            "to_address",
                            "value",
                            "gas_price",
                            "gas_limit",
                            "nonce",
                            "input"
                        ]
                    }
                }
            },
            "required": ["page", "pages", "result"]
        }
    },
    {
        "uri": "/gas-price",
        "method": "GET",
        "description": "Get details and estimates on the current gas prices",
        "request": {
            "title": "Request",
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "description": "The type of calculation to do.  Options: average, mean"
                },
                "block_length": {
                    "type": "number",
                    "description": "How many previous blocks to use in the calculation."
                }
            }
        },
        "response": {
            "title": "Response",
            "type": "object",
            "properties": {
                "results": {
                    "type": "number",
                    "description": "The gas price in wei",
                }
            },
            "required": ["results"]
        }
    },
]