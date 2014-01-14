#generic imports
import logging
import os
import sys
import unittest
ROOTPATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not ROOTPATH in sys.path:
    sys.path.append(ROOTPATH)
from sloSLOJSONRPC import SLOSLOJSONRPCError, SLOJSONRPC, SLOSLOJSONRPCNotification


class api(object):
    a = True

    @SLOSLOJSONRPCNotification
    def do(self, session):
        pass

    def ping(self, session):
        return 'pong'

    def one(self, session, r):
        return r

    def pong(self, session, a, b):
        return a + b

    def defping(self, session, a, b='a'):
        return a+b

    def invalid_error(self, session):
        raise SLOSLOJSONRPCError(-1)

    def internal_error(self, session):
        raise SLOSLOJSONRPCError(-32001)

    def uncaught_exception(self, session):
        raise StandardError('Uncaught Exception')


class sessionfaker(object):
    def __call__(self):
        class fakesession:
            def close(self):
                pass
        return fakesession()


class SLOJSONRPCTest(unittest.TestCase):
    def setUp(self):
        self.SLOJSONRPC = SLOJSONRPC(sessionfaker())
        self.api = api()
        self.SLOJSONRPC.register(api())

    def test_notification(self):
        self.assertEqual(None, self.SLOJSONRPC.handle_request({
            'SLOJSONRPC': '2.0', 'method': 'do'
        }))

    def test_noparam(self):
        self.assertEqual('pong', self.SLOJSONRPC.handle_request({
            'SLOJSONRPC': '2.0', 'method': 'ping', 'id': 1
        })['result'])

    def test_oneparam(self):
        self.assertEqual('pang', self.SLOJSONRPC.handle_request({
            'SLOJSONRPC': '2.0', 'method': 'one', 'id': 1, 'params': 'pang'
        })['result'])

    def test_multiparam(self):
        self.assertEqual('abcd', self.SLOJSONRPC.handle_request({
            'SLOJSONRPC': '2.0', 'method': 'pong',
            'id': 1, 'params': {'a': 'ab', 'b': 'cd'}
        })['result'])

    def test_multiparam_defaults(self):
        self.assertEqual('aba', self.SLOJSONRPC.handle_request({
            'SLOJSONRPC': '2.0', 'method': 'defping',
            'id': 1, 'params': {'a': 'ab'}
        })['result'])

    def test_integrated_ping(self):
        self.SLOJSONRPC = SLOJSONRPC(sessionfaker())
        self.assertEqual('pong', self.SLOJSONRPC.handle_request({
            'SLOJSONRPC': '2.0', 'method': 'ping', 'id': 1
        })['result'])

    def test_invalid_error(self):
        self.assertEqual(-32603, self.SLOJSONRPC.handle_request({
            'SLOJSONRPC': '2.0', 'method': 'invalid_error', 'id': 1
        })['error']['code'])

    def test_internal_error(self):
        self.assertEqual(-32001, self.SLOJSONRPC.handle_request({
            'SLOJSONRPC': '2.0', 'method': 'internal_error', 'id': 1
        })['error']['code'])

    def test_uncaught_exception(self):
        self.assertEqual(-32603, self.SLOJSONRPC.handle_request({
            'SLOJSONRPC': '2.0', 'method': 'uncaught_exception', 'id': 1
        })['error']['code'])


class SLOJSONRPCTestString(unittest.TestCase):
    def setUp(self):
        self.SLOJSONRPC = SLOJSONRPC(sessionfaker())
        self.api = api()
        self.SLOJSONRPC.register(api())

    def test_request(self):
        self.assertEqual(
            '{"SLOJSONRPC": "2.0", "id": 1, "result": "pong"}',
            self.SLOJSONRPC.handle_string(
                '{"SLOJSONRPC": "2.0", "method": "ping", "id": 1}')
        )

    def test_invalidjson(self):
        self.assertEqual(
            '{"SLOJSONRPC": "2.0", "id": null, ' +
            '"error": {"message": "Parse error", "code": -32700}}',
            self.SLOJSONRPC.handle_string(
                '"SLOJSONRPC": "2.0", "method": "ping", "id": 1')
        )

    def test_multiple_requests(self):
        self.assertEqual(
            '[{"SLOJSONRPC": "2.0", "id": 1, "result": "pong"},' +
            '{"SLOJSONRPC": "2.0", "id": 2, "result": "2"}]',
            self.SLOJSONRPC.handle_string(
                '[{"SLOJSONRPC": "2.0", "method": "ping", "id": 1},' +
                '{"SLOJSONRPC": "2.0", "method": "one", "id": 2, "params": "2"}]')
        )

    def test_multiple_requests_one_nodict(self):
        self.assertEqual(
            '{"SLOJSONRPC": "2.0", "id": null, "error":' +
            '{"message": "Parse error", "code": -32700}}',
            self.SLOJSONRPC.handle_string(
                '[{"SLOJSONRPC": "2.0", "method": "ping", "id": 1},[]]')
        )

    def test_multiple_requests_one_invalid(self):
        self.assertEqual(
            '{"SLOJSONRPC": "2.0", "id": null, "error": ' +
            '{"message": "Invalid Request", "code": -32600}}',
            self.SLOJSONRPC.handle_string(
                '[{"SLOJSONRPC": "2.0", "method": "ping", "id": 1},' +
                '{"method": "bla"}]')
        )

    def test_invalidtype(self):
        self.assertEqual(
            '{"SLOJSONRPC": "2.0", "id": null, "error": ' +
            '{"message": "Parse error", "code": -32700}}',
            self.SLOJSONRPC.handle_string('2')
        )


class SLOJSONRPCTestValidateParameters(unittest.TestCase):
    def setUp(self):
        self.SLOJSONRPC = SLOJSONRPC(sessionfaker())
        self.api = api()
        self.SLOJSONRPC.register(api())

    def test_invalid_method(self):
        self.assertEqual(-32601,
                         self.SLOJSONRPC.handle_request(
                         {'SLOJSONRPC': '2.0', 'method': 'fdsa'}
                         )
                         ['error']['code'])

    def test_too_many_params(self):
        self.assertEqual(-32602, self.SLOJSONRPC.handle_request({
            'SLOJSONRPC': '2.0', 'method': 'ping',
            'params': {'a': 1, 'b': 1, 'c': 2}, 'id': 1
        })['error']['code'])

    def test_too_many_params_no_param_method(self):
        self.assertEqual(-32602, self.SLOJSONRPC.handle_request({
            'SLOJSONRPC': '2.0', 'method': 'ping', 'params': {'a': 1}, 'id': 1
        })['error']['code'])

    def test_not_enough_params(self):
        self.assertEqual(-32602, self.SLOJSONRPC.handle_request({
            'SLOJSONRPC': '2.0', 'method': 'pong', 'params': {'a': 1}, 'id': 1
        })['error']['code'])

    def test_no_params(self):
        self.assertEqual(-32602, self.SLOJSONRPC.handle_request({
            'SLOJSONRPC': '2.0', 'method': 'pong', 'id': 1
        })['error']['code'])

    def test_invalid_params(self):
        self.assertEqual(-32602, self.SLOJSONRPC.handle_request({
            'SLOJSONRPC': '2.0', 'method': 'pong', 'params': 1, 'id': 1
        })['error']['code'])

    def test_id_in_notification(self):
        self.assertEqual(-32602, self.SLOJSONRPC.handle_request({
            'SLOJSONRPC': '2.0', 'method': 'do', 'id': 1
        })['error']['code'])

    def test_no_id_in_non_notification(self):
        self.assertEqual(-32602, self.SLOJSONRPC.handle_request({
            'SLOJSONRPC': '2.0', 'method': 'ping'
        })['error']['code'])


class SLOJSONRPCTestValidateFormat(unittest.TestCase):
    def setUp(self):
        self.SLOJSONRPC = SLOJSONRPC(sessionfaker())

    def test_no_SLOJSONRPC(self):
        try:
            self.SLOJSONRPC._validate_format({'method': 'do'})
        except SLOSLOJSONRPCError as err:
            self.assertEqual(err.errorcode, -32600)
        else:
            self.fail('Expected Error')

    def test_no_method(self):
        try:
            self.SLOJSONRPC._validate_format({'SLOJSONRPC': '2.0'})
        except SLOSLOJSONRPCError as err:
            self.assertEqual(err.errorcode, -32600)
        else:
            self.fail('Expected Error')

    def test_wrong_version(self):
        try:
            self.SLOJSONRPC._validate_format({'SLOJSONRPC': '2.1', 'method': 'do'})
        except SLOSLOJSONRPCError as err:
            self.assertEqual(err.errorcode, -32600)
        else:
            self.fail('Expected Error')

    def test_invalid_key(self):
        try:
            self.SLOJSONRPC._validate_format({'SLOJSONRPC': '2.1',
                                           'method': 'do', 'fd': None})
        except SLOSLOJSONRPCError as err:
            self.assertEqual(err.errorcode, -32600)
        else:
            self.fail('Expected Error')


class fake_request:
        def __init__(self, method, body):
            self.method = method

            class fake_body:
                def __init__(self, body):
                    self.body = body

                def read(self):
                    return self.body
            self.body = fake_body(body)


class SLOJSONRPCTestCherryPy(unittest.TestCase):
    def setUp(self):
        self.SLOJSONRPC = SLOJSONRPC(sessionfaker())

    def test_request(self):
        import cherrypy
        cherrypy.request = fake_request(
            'PUT', '{"SLOJSONRPC": "2.0", "method": "ping", "id": 1}')
        self.assertEqual(
            '{"SLOJSONRPC": "2.0", "id": 1, "result": "pong"}', self.SLOJSONRPC())

    def test_invalid_method(self):
        import cherrypy
        cherrypy.request = fake_request(
            'PUT', '{"SLOJSONRPC": "2.0", "method": "ping", "id": 1}')
        self.assertEqual(
            '{"SLOJSONRPC": "2.0", "id": 1, "result": "pong"}', self.SLOJSONRPC())
        cherrypy.request = fake_request(
            'POST', '{"SLOJSONRPC": "2.0", "method": "ping", "id": 1}')
        self.assertEqual(
            '{"SLOJSONRPC": "2.0", "id": 1, "result": "pong"}', self.SLOJSONRPC())
        cherrypy.request = fake_request(
            'PUTT', '{"SLOJSONRPC": "2.0", "method": "ping", "id": 1}')
        self.assertEqual('Method "PUTT" not allowed.', self.SLOJSONRPC())

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main(verbosity=20)
