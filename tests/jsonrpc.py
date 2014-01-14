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


class JSONRPCTest(unittest.TestCase):
    def setUp(self):
        api = getapi()
        self.jsonrpc = SLOJSONRPC(sessionfaker())
        self.api = api()
        self.jsonrpc.register(api())

    def test_notification(self):
        self.assertEqual(None, self.jsonrpc.handle_request({
            'jsonrpc': '2.0', 'method': 'do'
        }))

    def test_noparam(self):
        self.assertEqual('pong', self.jsonrpc.handle_request({
            'jsonrpc': '2.0', 'method': 'ping', 'id': 1
        })['result'])

    def test_oneparam(self):
        self.assertEqual('pang', self.jsonrpc.handle_request({
            'jsonrpc': '2.0', 'method': 'one', 'id': 1, 'params': 'pang'
        })['result'])

    def test_multiparam(self):
        self.assertEqual('abcd', self.jsonrpc.handle_request({
            'jsonrpc': '2.0', 'method': 'pong',
            'id': 1, 'params': {'a': 'ab', 'b': 'cd'}
        })['result'])

    def test_multiparam_defaults(self):
        self.assertEqual('aba', self.jsonrpc.handle_request({
            'jsonrpc': '2.0', 'method': 'defping',
            'id': 1, 'params': {'a': 'ab'}
        })['result'])

    def test_integrated_ping(self):
        self.jsonrpc = SLOJSONRPC(sessionfaker())
        self.assertEqual('pong', self.jsonrpc.handle_request({
            'jsonrpc': '2.0', 'method': 'ping', 'id': 1
        })['result'])

    def test_invalid_error(self):
        self.assertEqual(-32603, self.jsonrpc.handle_request({
            'jsonrpc': '2.0', 'method': 'invalid_error', 'id': 1
        })['error']['code'])

    def test_internal_error(self):
        self.assertEqual(-32001, self.jsonrpc.handle_request({
            'jsonrpc': '2.0', 'method': 'internal_error', 'id': 1
        })['error']['code'])

    def test_uncaught_exception(self):
        self.assertEqual(-32603, self.jsonrpc.handle_request({
            'jsonrpc': '2.0', 'method': 'uncaught_exception', 'id': 1
        })['error']['code'])
