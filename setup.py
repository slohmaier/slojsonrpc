from setuptools import setup
setup(
    name='slojsonrpc',
    packages=['slojsonrpc'],
    version=1.0,
    description='Universal JSONrpc handler, that maps class-methods to jsonrpc-methods.',
    author='Stefan Lohmaier',
    url='https://github.com/StefanLohmaier/slojsonrpc',
    keywords=['jsonrpc'],
    test_suite='tests',
    install_requires='cherrypy',
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    long_description='''
slojsonrpc
----------

Universal JSONrpc handler, that maps class-methods to jsonrpc-methods.
 - registers common classmethods and reads their function signature
 - check for jsonrpc compliance
 - checks parameters against function signature
 - method parameters with defaults are optional
 - creates db-sessions for each method call

Example:

class test:
    def testmethod(self, session , a, b=1):
        ...

regiter with:
SLOJSONrpc.register()

Will be mapped to jsonrpcmethod:
{'jsonrpc': '2.0', 'method': 'testmethod', params: {'a': 42} }
    '''
)
