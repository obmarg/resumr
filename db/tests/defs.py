import unittest
import mox
from collections import namedtuple


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()

TestBlobType = namedtuple( 'TestBlobType', [ 'data' ] )
TestCommitType = namedtuple( 'TestCommitType', [ 'tree', 'oid', 'parents' ] )
TestObjectType = namedtuple( 'TestObjectType', 'oid' )


def StubOutConstructor( mox, cls, func=None ):
    '''
    Mocks out the constructor of a class then hides the mock so there's no
    verification.  For use when we're calling the constructor ourselves but not
    actually wanting to test anything going on in the constructor

    Since we use the mox StubOutWithMock function, calling UnsetStubs will
    replace the constructor with the original

    Params:
        mox     Our current Mox instance
        cls     The class to stub out
        func    An optional func to replace the constructor with
                If not passed, will be a no-op function
    '''
    # Stub out the constructor so it gets reset
    mox.StubOutWithMock( cls, '__init__' )
    # Then replace it with a lambda, so it doesn't get validated
    if func:
        cls.__init__ = func
    else:
        cls.__init__ = lambda *pos, **kw: None



