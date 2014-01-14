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

from slojsonrpc import SLOJSONRPCError, SLOJSONRPCNotification


def getapi():
    class api(object):
        a = True

        @SLOJSONRPCNotification
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
            raise SLOJSONRPCError(-1)

        def internal_error(self, session):
            raise SLOJSONRPCError(-32001)

        def uncaught_exception(self, session):
            raise StandardError('Uncaught Exception')
    return api


class sessionfaker(object):
    def __call__(self):
        class fakesession:
            def close(self):
                pass
        return fakesession()
