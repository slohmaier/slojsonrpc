'''
The MIT License (MIT)

Copyright (c) 2014 Stefan Lohmaier

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import json
import unittest
from slojsonrpc import SLOJSONRPC
from .api import getapi, sessionfaker


class JSONRPCTestString(unittest.TestCase):
    def setUp(self):
        api = getapi()
        self.jsonrpc = SLOJSONRPC(sessionfaker())
        self.api = api()
        self.jsonrpc.register(api())

    def test_request(self):
        self.assertEqual(
            json.loads('{"jsonrpc": "2.0", "id": 1, "result": "pong"}'),
            json.loads(self.jsonrpc.handle_string('{"jsonrpc": "2.0", "method": "ping", "id": 1}'))
        )

    def test_invalidjson(self):
        self.assertEqual(
            json.loads('{"jsonrpc": "2.0", "id": null, "error": {"message": "Parse error", "code": -32700}}'),
            json.loads(self.jsonrpc.handle_string('"jsonrpc": "2.0", "method": "ping", "id": 1'))
        )

    def test_multiple_requests(self):
        self.assertEqual(
            json.loads('[{"jsonrpc": "2.0", "id": 1, "result": "pong"},{"jsonrpc": "2.0", "id": 2, "result": "2"}]'),
            json.loads(self.jsonrpc.handle_string('[{"jsonrpc": "2.0", "method": "ping", "id": 1},' +
                                                  '{"jsonrpc": "2.0", "method": "one", "id": 2, "params": "2"}]'))
        )

    def test_multiple_requests_one_nodict(self):
        self.assertEqual(
            json.loads('{"jsonrpc": "2.0", "id": null, "error":{"message": "Parse error", "code": -32700}}'),
            json.loads(self.jsonrpc.handle_string('[{"jsonrpc": "2.0", "method": "ping", "id": 1},[]]'))
        )

    def test_multiple_requests_one_invalid(self):
        self.assertEqual(
            json.loads('{"jsonrpc": "2.0", "id": null, "error": {"message": "Invalid Request", "code": -32600}}'),
            json.loads(self.jsonrpc.handle_string('[{"jsonrpc": "2.0", "method": "ping", "id": 1},{"method": "bla"}]'))
        )

    def test_invalidtype(self):
        self.assertEqual(
            json.loads('{"jsonrpc": "2.0", "id": null, "error": {"message": "Parse error", "code": -32700}}'),
            json.loads(self.jsonrpc.handle_string('2'))
        )
