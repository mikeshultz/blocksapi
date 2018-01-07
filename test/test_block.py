import pytest
import requests
import threading
import json
from datetime import datetime
from dateutil.parser import parse
from blocksapi.web import Application, IOLoop
    
TEST_PORT = 8081
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

def is_valid_block_schema(blk):
    """ Test that an object is the correct schema for a block """

    try:
        assert 'block_number' in blk
        assert 'block_timestamp' in blk
        assert 'hash' in blk
        assert 'miner' in blk
        assert 'nonce' in blk
        assert 'difficulty' in blk
        assert 'gas_used' in blk
        assert 'gas_limit' in blk
        assert 'size' in blk
        return True
    except AssertionError:
        return False

@pytest.yield_fixture(scope="session")
def server():
    yield start()
    return stop()

class TestBlock(object):
    def make_call(self, server, payload):
        """ Make an API call to the /block endpoint """
        return requests.get('{}/block'.format(server), data=json.dumps(payload))

    def test_block_number(self, server):
        """ Test /block with a block_number parameter """

        req = self.make_call(server, { 'block_number': 123 })

        assert req.status_code == 200

        resp = req.json()

        # Make sure the output is sane
        assert 'results' in resp
        assert len(resp['results']) == 1
        assert is_valid_block_schema(resp['results'][0])

        # Make sure values look good
        assert resp['results'][0]['block_number'] == 123
        #TODO: Fix this! https://github.com/mikeshultz/blocks/issues/2
        #assert parse(resp['results'][0]['block_timestamp']) == datetime.fromtimestamp(1438270492)
        assert resp['results'][0]['hash'] == '0x37cb73b97d28b4c6530c925d669e4b0e07f16e4ff41f45d10d44f4c166d650e5'
        assert resp['results'][0]['miner'].lower() == '0xbb7b8287f3f0a933474a79eae42cbca977791171'
        assert hex(resp['results'][0]['nonce']) == '0x18c851620e8d6cb6'
        assert resp['results'][0]['difficulty'] == 18118731572
        assert resp['results'][0]['gas_used'] == 0
        assert resp['results'][0]['gas_limit'] == 5000
        assert resp['results'][0]['size'] == 542

    def test_block_range(self, server):
        """ Test /block with a start and end parameters """

        req = self.make_call(server, { 'start': 123, 'end': 132 })

        assert req.status_code == 200

        resp = req.json()

        # Make sure the output is sane
        assert 'results' in resp
        assert len(resp['results']) == 10
        for blk in resp['results']:
            assert is_valid_block_schema(blk)

    def test_block_range_date(self, server):
        """ Test /block with a start_time and end_time parameters """

        start_time = parse('2016-01-01 00:00:00').isoformat()
        end_time = parse('2016-01-01 00:10:00').isoformat()

        req = self.make_call(server, { 'start_time': start_time, 'end_time': end_time })

        assert req.status_code == 200

        resp = req.json()

        # Make sure the output is sane
        assert 'results' in resp
        assert len(resp['results']) == 49
        for blk in resp['results']:
            assert is_valid_block_schema(blk)

    def test_invalid_block_requests(self, server):
        """ Test /block with invalid parameters """

        start_time = parse('2016-01-01 00:00:00').isoformat()
        end_time = parse('2016-01-01 00:10:00').isoformat()

        req = self.make_call(server, { 'start_time': start_time })
        assert req.status_code == 400

        req = self.make_call(server, { 'end_time': end_time })
        assert req.status_code == 400

        req = self.make_call(server, { 'start_time': start_time })
        assert req.status_code == 400

        req = self.make_call(server, { 'start_time': start_time, 'end': 3000000 })
        assert req.status_code == 400

        req = self.make_call(server, { 'nothing': start_time, 'something': end_time })
        assert req.status_code == 400

        req = self.make_call(server, { 'start': 123 })
        assert req.status_code == 400

        req = self.make_call(server, { 'end': 123 })
        assert req.status_code == 400

        req = self.make_call(server, { 'end': 123 })
        assert req.status_code == 400

        req = self.make_call(server, { 'block_number': "abc" })
        assert req.status_code == 400


    def test_block_not_found(self, server):
        """ Test /block parameters that don't match """

        FUTURE_BLOCK = 999999999
        FUTURE_DATE1 = parse('3016-01-01 00:10:00').isoformat()
        FUTURE_DATE2 = parse('4016-01-01 00:10:00').isoformat()

        # Some theoretical future block_number that doesn't exist
        req = self.make_call(server, { 'block_number': FUTURE_BLOCK })
        assert req.status_code == 404

        # Some theoretical future block_number that doesn't exist
        req = self.make_call(server, { 'start': FUTURE_BLOCK, 'end': FUTURE_BLOCK+1 })
        assert req.status_code == 404

        # Some theoretical future block_number that doesn't exist
        req = self.make_call(server, { 'start_time': FUTURE_DATE1, 'end_time': FUTURE_DATE2 })
        assert req.status_code == 404


