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
from slojsonrpc import SLOJSONRPC, SLOJSONRPCError
from .api import sessionfaker


class JSONRPCTestValidateFormat(unittest.TestCase):
    def setUp(self):
        self.jsonrpc = SLOJSONRPC(sessionfaker())

    def test_no_jsonrpc(self):
        try:
            self.jsonrpc._validate_format({'method': 'do'})
        except SLOJSONRPCError as err:
            self.assertEqual(err.errorcode, -32600)
        else:
            self.fail('Expected Error')

    def test_no_method(self):
        try:
            self.jsonrpc._validate_format({'jsonrpc': '2.0'})
        except SLOJSONRPCError as err:
            self.assertEqual(err.errorcode, -32600)
        else:
            self.fail('Expected Error')

    def test_wrong_version(self):
        try:
            self.jsonrpc._validate_format({'jsonrpc': '2.1', 'method': 'do'})
        except SLOJSONRPCError as err:
            self.assertEqual(err.errorcode, -32600)
        else:
            self.fail('Expected Error')

    def test_invalid_key(self):
        try:
            self.jsonrpc._validate_format({'jsonrpc': '2.1',
                                           'method': 'do', 'fd': None})
        except SLOJSONRPCError as err:
            self.assertEqual(err.errorcode, -32600)
        else:
            self.fail('Expected Error')
