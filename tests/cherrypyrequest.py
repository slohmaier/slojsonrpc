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
from .api import sessionfaker

try:
    import cherrypy

    class fake_request:
            def __init__(self, method, body):
                self.method = method

                class fake_body:
                    def __init__(self, body):
                        self.body = body

                    def read(self):
                        return self.body
                self.body = fake_body(body)

    class JSONRPCTestCherryPy(unittest.TestCase):
        def setUp(self):
            self.jsonrpc = SLOJSONRPC(sessionfaker())

        def test_request(self):
            cherrypy.request = fake_request(
                'PUT', '{"jsonrpc": "2.0", "method": "ping", "id": 1}')
            self.assertEqual(
                json.loads('{"jsonrpc": "2.0", "id": 1, "result": "pong"}'),
                json.loads(self.jsonrpc()))

        def test_invalid_method(self):
            cherrypy.request = fake_request(
                'PUT', '{"jsonrpc": "2.0", "method": "ping", "id": 1}')
            self.assertEqual(
                json.loads('{"jsonrpc": "2.0", "id": 1, "result": "pong"}'),
                json.loads(self.jsonrpc()))
            cherrypy.request = fake_request(
                'POST', '{"jsonrpc": "2.0", "method": "ping", "id": 1}')
            self.assertEqual(
                json.loads('{"jsonrpc": "2.0", "id": 1, "result": "pong"}'),
                json.loads(self.jsonrpc()))
            cherrypy.request = fake_request(
                'PUTT', '{"jsonrpc": "2.0", "method": "ping", "id": 1}')
            self.assertEqual('Method "PUTT" not allowed.', self.jsonrpc())
except:
    pass
