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

import inspect
import json
import logging
import traceback


def SLOJSONRPCNotification(fct):
    '''
    Decorate a JSONRPC method to be a notification and so have no return value.
    '''
    fct.__SLOJSONRPCNotification__ = True
    return fct


class SLOJSONRPCError(BaseException):
    '''
    Reprents an JSONRPC error code.
    '''

    #messages for standard errors
    _default_messages = {
        -32600: 'Invalid Request',
        -32601: 'Method not found',
        -32602: 'Invalid params',
        -32603: 'Internal error',
        -32700: 'Parse error'
    }

    def __init__(self, errorcode, message=None):
        '''
        create a SLOJSONRPCError

        errorcode - errcode as integer
        message - message for the error (default: None)
        '''
        self.errorcode = errorcode

        if not errorcode in SLOJSONRPCError._default_messages \
           and (errorcode > -32000 or errorcode < -32099):
            raise SLOJSONRPCError(-32603)

        if errorcode in SLOJSONRPCError._default_messages:
            self.message = SLOJSONRPCError._default_messages[errorcode]
        else:
            self.message = message

    def to_json(self, id=None):
        '''
        convert SLOJSONRPCError to a json-dictionary object

        id - message id (default: None)

        returns json-dictionary
        '''
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': self.errorcode,
                'message': self.message
            },
            'id': id
        }


class SLOJSONRPC(object):
    '''
    SLOJSONRPC implementation.

    Can be a cherrypy url handler:
    class Root:
        jsonrpc = SLOJSONRPC(sessionmaker)
    '''

    def __init__(self, sessionmaker):
        '''
        create a new SLOJSONRPC

        sessionmaker - default argument for all methods
        '''
        self._sessionmaker = sessionmaker
        self._methods = {
            'ping': {
                'argspec': inspect.getargspec(self.ping),
                'fct': self.ping
            }
        }

    def ping(self, session):
        '''Default ping method'''
        return 'pong'

    def register(self, obj):
        '''
        register all methods for of an object as json rpc methods

        obj - object with methods
        '''
        for method in dir(obj):
            #ignore private methods
            if not method.startswith('_'):
                fct = getattr(obj, method)
                #only handle functions
                try:
                    getattr(fct, '__call__')
                except AttributeError:
                    pass
                else:
                    logging.debug('JSONRPC: Found Method: "%s"' % method)
                    self._methods[method] = {
                        'argspec': inspect.getargspec(fct),
                        'fct': fct
                    }

    #keys a jsonrpc-dict must have
    _min_keys = ['jsonrpc', 'method']
    #keys a jsonrpc-dict can have
    _optional_keys = ['params', 'id']
    #keys that are allowed
    _allowed_keys = _min_keys + _optional_keys

    @staticmethod
    def _validate_format(req):
        '''
        Validate jsonrpc compliance of a jsonrpc-dict.

        req - the request as a jsonrpc-dict

        raises SLOJSONRPCError on validation error
        '''
        #check for all required keys
        for key in SLOJSONRPC._min_keys:
            if not key in req:
                logging.debug('JSONRPC: Fmt Error: Need key "%s"' % key)
                raise SLOJSONRPCError(-32600)

        #check all keys if allowed
        for key in req.keys():
            if not key in SLOJSONRPC._allowed_keys:
                logging.debug('JSONRPC: Fmt Error: Not allowed key "%s"' % key)
                raise SLOJSONRPCError(-32600)

        #needs to be jsonrpc 2.0
        if req['jsonrpc'] != '2.0':
            logging.debug('JSONRPC: Fmt Error: "jsonrpc" needs to be "2.0"')
            raise SLOJSONRPCError(-32600)

    def _validate_params(self, req):
        '''
        Validate parameters of a jsonrpc-request.

        req - request as a jsonrpc-dict

        raises SLOJSONRPCError on validation error
        '''

        #does the method exist?
        method = req['method']
        if not method in self._methods:
            raise SLOJSONRPCError(-32601)
        fct = self._methods[method]['fct']

        #'id' is only needed for none SLOJSONRPCNotification's
        try:
            getattr(fct, '__SLOJSONRPCNotification__')
            if 'id' in req:
                logging.debug('JSONRPC: Fmt Error: no id for SLOJSONRPCNotifications')
                raise SLOJSONRPCError(-32602)
        except AttributeError:
            if not 'id' in req:
                logging.debug('JSONRPC: Fmt Error: Need an id for non SLOJSONRPCNotifications')
                raise SLOJSONRPCError(-32602)

        #get arguments and defaults for the python-function representing
        # the method
        argspec = self._methods[method]['argspec']
        args, defaults = list(argspec.args), \
            list(argspec.defaults if argspec.defaults else [])

        #ignore self and session
        if 'self' in args:
            args.remove('self')
        args.remove('session')

        #create required arguments. delete the ones with defaults
        required = list(args)
        if defaults:
            for default in defaults:
                required.pop()

        #check if we need paremeters and there are none, then error
        if len(required) > 0 and 'params' not in req:
            logging.debug('JSONRPC: Parameter Error: More than zero params required')
            raise SLOJSONRPCError(-32602)

        if 'params' in req:
            #parameters must be a dict if there is more then one
            if not isinstance(req['params'], dict) and len(required) > 1:
                logging.debug('JSONRPC: Parameter Error: "params" must be a dictionary')
                raise SLOJSONRPCError(-32602)

            if isinstance(req['params'], dict):
                #check if required parameters are there
                for key in required:
                    if not key in req['params']:
                        logging.debug('JSONRPC: Parameter Error: Required key "%s" is missing' % key)
                        raise SLOJSONRPCError(-32602)

                #check if parameters are given that do not exist in the method
                for key in req['params']:
                    if not key in required:
                        logging.debug('JSONRPC: Parameter Error: Key is not allowed "%s"' % key)
                        raise SLOJSONRPCError(-32602)

    def handle_request(self, req, validate=True):
        '''
        handle a jsonrpc request

        req - request as jsonrpc-dict
        validate - validate the request? (default: True)

        returns jsonrpc-dict with result or error
        '''

        #result that will be filled and returned
        res = {'jsonrpc': '2.0', 'id': -1, 'result': None}

        logging.debug('')
        logging.debug('--------------------REQUEST' +
                      '--------------------\n' +
                      json.dumps(req,
                                 sort_keys=True,
                                 indent=4,
                                 separators=(',', ': ')))
        logging.debug('-----------------------------------------------')

        notification = False
        session = self._sessionmaker()
        try:
            #validate request
            if validate:
                self._validate_format(req)
                self._validate_params(req)

            method = req['method']

            #check if request is a notification
            try:
                getattr(self._methods[method]['fct'], '__SLOJSONRPCNotification__')
                notification = True
            except AttributeError:
                notification = False

            #call the python function
            if 'params' in req:
                fct = self._methods[method]['fct']
                if isinstance(req['params'], dict):
                    req['params']['session'] = session
                    res['result'] = fct(**req['params'])
                else:
                    res['result'] = fct(session, req['params'])
            else:
                res['result'] = self._methods[method]['fct'](session)
        except SLOJSONRPCError as e:
            res = e.to_json(req.get('id', None))
        except:
            logging.debug('Uncaught Exception:')
            logging.debug('-------------------\n' + traceback.format_exc())
            res = SLOJSONRPCError(-32603).to_json(req.get('id', None))

        session.close()

        logging.debug('--------------------RESULT' +
                      '--------------------\n' +
                      json.dumps(res,
                                 sort_keys=True,
                                 indent=4,
                                 separators=(',', ': ')))
        logging.debug('----------------------------------------------')

        #return None if a notification
        if notification:
            return None
        elif not 'error' in res:
            res['id'] = req['id']

        return res

    def handle_string(self, strreq):
        '''
        Handle a string representing a jsonrpc-request

        strreq - jsonrpc-request as a string

        returns jsonrpc-response as a string
        '''

        #convert to jsonrpc-dict
        req = None
        try:
            req = json.loads(strreq)
        except:
            logging.debug('JSONRPC: Format Exception:')
            logging.debug('-----------------\n' + traceback.format_exc())
            return json.dumps(SLOJSONRPCError(-32700).to_json())

        #handle single request
        if isinstance(req, dict):
            return json.dumps(self.handle_request(req))
        #handle multiple requests
        elif isinstance(req, list):
            for r in req:
                if not isinstance(r, dict):
                    logging.debug('JSONRPC: Fmt Error: Item ' +
                                  '"%s" in request is no dictionary.' % str(r))
                    return json.dumps(SLOJSONRPCError(-32700).to_json())
                try:
                    self._validate_format(r)
                    self._validate_params(r)
                except SLOJSONRPCError as e:
                    return json.dumps(e.to_json(r.get('id', None)))

            res = []
            for r in req:
                res.append(self.handle_request(r, validate=False))
            return json.dumps(res)
        #invalid request
        else:
            return json.dumps(SLOJSONRPCError(-32700).to_json())


try:
    import cherrypy
    #mark as exposed for cherrypy
    SLOJSONRPC.exposed = True

        #default handler for cherrypy
    def __slojsonrpccall__(self):
        if cherrypy.request.method in ['POST', 'PUT']:
            return self.handle_string(cherrypy.request.body.read())
        else:
            return 'Method "%s" not allowed.' % cherrypy.request.method

    SLOJSONRPC.__call__ = __slojsonrpccall__

except:
    pass
