
import pygit2
from .. import gitutils
from .defs import BaseTest, TestObjectType, TestBlobType, TestCommitType


class ContentTestsMeta(type):
    '''
    Meta class for ContentTests

    Renames the _testBlah methods in ContentTests to testBlah in any
    subclasses of ContentTests.  This means that classes inheriting
    from ContentTests will run the tests contained in ContentTests,
    but ContentTests itself will not be considered an actual unit test
    '''

    def __new__(meta, className, bases, classDict):
        if className != 'ContentTests':
            # Find the ContentTests base
            for cls in bases:
                if cls.__name__ != 'ContentTests':
                    continue
                # Then add the _test methods to our class dict
                # without the _ prefix
                for attrName, attr in cls.__dict__.items():
                    if attrName.startswith( '_test' ):
                        classDict[attrName[1:]] = attr
        return type.__new__(meta, className, bases, classDict)


class ContentTests(BaseTest):
    '''
    This class provides tests for the base Content class functionality.

    It is not intended to be used directly, as the Content class only
    really works when it is created as a subclass.

    To use this class, you should inherit from it in the class that
    tests your object, providing the name of the actual class to
    test in the TestClassType class variable.  For example:

        class SectionTests(ContentTests):
            TestClassType = Section

    '''
    TestClassType = None

    __metaclass__ = ContentTestsMeta

    def setUp(self):
        super( ContentTests, self ).setUp()
        self.mox.StubOutWithMock(gitutils, 'CommitBlob')

    def _testCurrentContent( self ):
        '''
        Tests the CurrentContent function
        '''
        mockHead = self.mox.CreateMock( pygit2.Commit )
        mockRepo = self.mox.CreateMock( pygit2.Repository )

        mockCommit = TestObjectType( 'blobOid' )

        mockHead.tree = self.mox.CreateMockAnything()

        mockHead.tree[ 0 ].AndReturn( mockCommit )

        mockBlob = TestBlobType( 'blobData' )

        mockRepo[ 'blobOid' ].AndReturn( mockBlob )

        self.mox.ReplayAll()

        s = self.TestClassType( 'name', mockHead, mockRepo )
        c = s.CurrentContent()

        self.mox.VerifyAll()
        self.assertEqual( 'blobData', c )

    def _testSetContent( self ):
        '''
        Tests the SetContent function
        '''
        mockHead = self.mox.CreateMock( pygit2.Commit )
        mockRepo = self.mox.CreateMock( pygit2.Repository )

        gitutils.CommitBlob(
                mockRepo, 'content', 'name', 'Updating section',
                [ mockHead ], 'refs/heads/sections/name'
                ).AndReturn( 'newId' )

        mockRepo[ 'newId' ].AndReturn( 'newCommit' )

        self.mox.ReplayAll()

        s = self.TestClassType( 'name', mockHead, mockRepo )
        s.SetContent( 'content' )

        self.mox.VerifyAll()
        self.assertEqual( s.headCommit, 'newCommit' )

    def _testContentHistory(self):
        '''
        Tests the ContentHistory function
        '''
        mockRepo = self.mox.CreateMock( pygit2.Repository )

        objects = [
                TestObjectType('oid1'),
                TestObjectType('oid2'),
                TestObjectType('oid3')
                ]
        secondParent = TestCommitType([objects[2]], '2ndParentOid', [])
        firstParent = TestCommitType(
                [objects[1]], '1stParentOid', [secondParent]
                )
        head = TestCommitType([objects[0]], 'headOid', [firstParent])

        expected = ['headData', '1stParentData', '2ndParentData']
        mockRepo['oid1'].AndReturn(TestBlobType(expected[0]))
        mockRepo['oid2'].AndReturn(TestBlobType(expected[1]))
        mockRepo['oid3'].AndReturn(TestBlobType(expected[2]))

        self.mox.ReplayAll()

        s = self.TestClassType('name', head, mockRepo)
        history = s.ContentHistory()
        self.assertEqual( expected, list(history))
