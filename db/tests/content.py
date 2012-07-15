
import pygit2
from .. import gitutils
from .defs import BaseTest, TestObjectType, TestBlobType, TestCommitType


class ContentTests(BaseTest):
    '''
    This class provides tests for the base Content class functionality.

    It is not intended to be used directly, as the Content class only
    really works when it is created as a subclass.

    To use this class, you should inherit from it in the class that
    tests your object, providing some test parameters as class variables.
    For example:

        class SectionTests(ContentTests):
            TestClass = Section
            CommitRefPrefix = 'refs/heads/sections'

    Class Variables:
        TestClass       The Content subclass we're testing
        CommitRefPrefix The prefix this class uses on refs when creating
                        a commit
        NameToUse       The name to pass to TestClass constructor (optional)
    '''
    TestClass = None
    CommitRefPrefix = None
    NameToUse = 'name'

    def setUp(self):
        super( ContentTests, self ).setUp()
        self.mox.StubOutWithMock(gitutils, 'CommitBlob')

    def testCurrentContent( self ):
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

        s = self.TestClass( self.NameToUse, mockHead, mockRepo )
        c = s.CurrentContent()

        self.mox.VerifyAll()
        self.assertEqual( 'blobData', c )

    def testSetContent( self ):
        '''
        Tests the SetContent function
        '''
        mockHead = self.mox.CreateMock( pygit2.Commit )
        mockRepo = self.mox.CreateMock( pygit2.Repository )

        gitutils.CommitBlob(
                mockRepo, 'content', self.NameToUse, 'Updating content',
                [ mockHead ], self.CommitRefPrefix + self.NameToUse
                ).AndReturn( 'newId' )

        mockRepo[ 'newId' ].AndReturn( 'newCommit' )

        self.mox.ReplayAll()

        s = self.TestClass( self.NameToUse, mockHead, mockRepo )
        s.SetContent( 'content' )

        self.mox.VerifyAll()
        self.assertEqual( s.headCommit, 'newCommit' )

    def testContentHistory(self):
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

        s = self.TestClass(self.NameToUse, head, mockRepo)
        history = s.ContentHistory()
        self.assertEqual( expected, list(history))
