import pytest
import requests
import threading
import json
from datetime import datetime
from dateutil.parser import parse
from blocksapi.web import Application, IOLoop
    
TEST_PORT = 8080
LOOP = IOLoop.instance()

def start():
    global thread, LOOP
    app = Application()
    app.listen(TEST_PORT)
    thread = threading.Thread(target=LOOP.start)
    thread.start()
    return "http://localhost:{}".format(TEST_PORT)

def stop():
    global thread, LOOP
    LOOP.add_callback(LOOP.stop)
    thread.join()

def is_valid_tx_schema(tx):
    """ Test that an object is the correct schema for a transaction """

    try:
        assert 'hash' in tx
        assert 'block_number' in tx
        assert 'from_address' in tx
        assert 'to_address' in tx
        assert 'value' in tx
        assert 'gas_price' in tx
        assert 'gas_limit' in tx
        assert 'nonce' in tx
        assert 'input' in tx
        return True
    except AssertionError:
        return False

@pytest.yield_fixture(scope="session")
def server():
    yield start()
    return stop()

class TestTransaction(object):
    def make_call(self, server, payload):
        """ Make an API call to the /block endpoint """
        return requests.get('{}/transaction'.format(server), data=json.dumps(payload))

    def test_tx_hash(self, server):
        """ Test /transaction with a hash parameter """

        req = self.make_call(server, { 'hash': '0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060' })

        assert req.status_code == 200

        resp = req.json()

        # Make sure the output is sane
        assert 'results' in resp
        assert len(resp['results']) == 1
        assert is_valid_tx_schema(resp['results'][0])

        # Make sure values look good
        assert resp['results'][0]['hash'] == '0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060'
        assert resp['results'][0]['block_number'] == 46147
        assert resp['results'][0]['from_address'] == '0xa1e4380a3b1f749673e270229993ee55f35663b4'
        assert resp['results'][0]['to_address'] == '0x5df9b87991262f6ba471f09758cde1c0fc1de734'
        assert resp['results'][0]['value'] == 31337
        assert resp['results'][0]['gas_price'] == 50000000000000
        assert resp['results'][0]['gas_limit'] == 21000
        assert resp['results'][0]['nonce'] == 0
        assert resp['results'][0]['input'] == "0x"

    def test_block(self, server):
        """ Test /transaction with a block_number parameter """

        req = self.make_call(server, { 'block_number': 46147 })

        assert req.status_code == 200

        resp = req.json()

        # Make sure the output is sane
        assert 'results' in resp
        assert len(resp['results']) == 1
        for tx in resp['results']:
            assert is_valid_tx_schema(tx)

    def test_to_address(self, server):
        """ Test /transaction with a to_address parameter """

        req = self.make_call(server, { 'to_address': '0x5DF9B87991262F6BA471F09758CDE1c0FC1De734' })

        assert req.status_code == 200

        resp = req.json()

        # Make sure the output is sane
        assert 'results' in resp
        assert len(resp['results']) == 2
        for tx in resp['results']:
            assert is_valid_tx_schema(tx)

    def test_from_address(self, server):
        """ Test /transaction with a from_address parameter """

        req = self.make_call(server, { 'from_address': '0xA1E4380A3B1f749673E270229993eE55F35663b4' })

        assert req.status_code == 200

        resp = req.json()

        # Make sure the output is sane
        assert 'results' in resp
        #assert len(resp['results']) == 2
        for tx in resp['results']:
            assert is_valid_tx_schema(tx)

    def test_invalid_transaction_requests(self, server):
        """ Test /transaction with invalid parameters """

        bad_hex = '0xDeadBEEF'
        
        req = self.make_call(server, { 'hash': bad_hex })
        assert req.status_code == 400
        
        req = self.make_call(server, { 'to_address': bad_hex })
        assert req.status_code == 400
        
        req = self.make_call(server, { 'from_address': bad_hex })
        assert req.status_code == 400


    def test_block_not_found(self, server):
        """ Test /transaction parameters that don't match """

        fake_hash = '0x0c300ff6aa5906693d58ccb778877f97056c12bf8c5a18f8a45ab5d61ba502f6'
        bad_address = '0x5DF9B87991262deadbeef09758CDE1c0FC1De734'
        addr_no_from = '0x5DF9B87991262F6BA471F09758CDE1c0FC1De734'

        # Some theoretical future block_number that doesn't exist
        req = self.make_call(server, { 'hash': fake_hash })
        assert req.status_code == 404

        # Some theoretical future block_number that doesn't exist
        req = self.make_call(server, { 'from_address': addr_no_from })
        assert req.status_code == 404

        # Some theoretical future block_number that doesn't exist
        req = self.make_call(server, { 'from_address': bad_address })
        assert req.status_code == 404


