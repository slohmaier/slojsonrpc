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

import unittest
from slojsonrpc import SLOJSONRPC
from .api import getapi, sessionfaker


class JSONRPCTestValidateParameters(unittest.TestCase):
    def setUp(self):
        api = getapi()
        self.jsonrpc = SLOJSONRPC(sessionfaker())
        self.api = api()
        self.jsonrpc.register(api())

    def test_invalid_method(self):
        self.assertEqual(-32601,
                         self.jsonrpc.handle_request(
                         {'jsonrpc': '2.0', 'method': 'fdsa'}
                         )
                         ['error']['code'])

    def test_too_many_params(self):
        self.assertEqual(-32602, self.jsonrpc.handle_request({
            'jsonrpc': '2.0', 'method': 'ping',
            'params': {'a': 1, 'b': 1, 'c': 2}, 'id': 1
        })['error']['code'])

    def test_too_many_params_no_param_method(self):
        self.assertEqual(-32602, self.jsonrpc.handle_request({
            'jsonrpc': '2.0', 'method': 'ping', 'params': {'a': 1}, 'id': 1
        })['error']['code'])

    def test_not_enough_params(self):
        self.assertEqual(-32602, self.jsonrpc.handle_request({
            'jsonrpc': '2.0', 'method': 'pong', 'params': {'a': 1}, 'id': 1
        })['error']['code'])

    def test_no_params(self):
        self.assertEqual(-32602, self.jsonrpc.handle_request({
            'jsonrpc': '2.0', 'method': 'pong', 'id': 1
        })['error']['code'])

    def test_invalid_params(self):
        self.assertEqual(-32602, self.jsonrpc.handle_request({
            'jsonrpc': '2.0', 'method': 'pong', 'params': 1, 'id': 1
        })['error']['code'])

    def test_id_in_notification(self):
        self.assertEqual(-32602, self.jsonrpc.handle_request({
            'jsonrpc': '2.0', 'method': 'do', 'id': 1
        })['error']['code'])

    def test_no_id_in_non_notification(self):
        self.assertEqual(-32602, self.jsonrpc.handle_request({
            'jsonrpc': '2.0', 'method': 'ping'
        })['error']['code'])
