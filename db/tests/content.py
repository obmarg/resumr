
import pygit2
from .. import gitutils
from .defs import BaseTest, TestObjectType, TestBlobType, TestCommitType
from ..errors import ContentNotFound


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
            CommitRefPrefix = "refs/heads/sections"

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

    def setupRepoForGetHeadCommit( self ):
        '''
        Prepares a mock repo for the calls expected to find the head commit of
        some content

        Returns:
            A tuple ( mockRepo, mockHeadCommit )
        '''
        mockHead = self.mox.CreateMock( pygit2.Commit )
        mockRepo = self.mox.CreateMock( pygit2.Repository )

        mockRepo.lookup_reference(
                self.CommitRefPrefix + self.NameToUse
                ).AndReturn( TestObjectType( 'oid' ) )
        mockRepo[ 'oid' ].AndReturn( mockHead )
        return (mockRepo, mockHead)

    def testCreate(self):
        '''
        Testing db.Content.Create with default content
        '''
        mockRepo = self.mox.CreateMock( pygit2.Repository )
        gitutils.CommitBlob(
                mockRepo, self.TestClass.DefaultContent, self.NameToUse,
                'Create content "{0}"'.format(self.NameToUse)
                ).AndReturn( 'commitId' )
        mockRepo.create_reference(
                self.CommitRefPrefix + self.NameToUse, 'commitId'
                ).AndReturn( 'reference' )

        self.mox.ReplayAll()

        s = self.TestClass( self.NameToUse, mockRepo )
        actual = s.Create()
        self.assertEqual( 'reference', actual )
        self.mox.VerifyAll()

    def testCreateWithContent(self):
        '''
        Testing db.Content.Create with actual content
        '''
        mockRepo = self.mox.CreateMock( pygit2.Repository )
        gitutils.CommitBlob(
                mockRepo, 'some content', self.NameToUse,
                'Create content "{0}"'.format(self.NameToUse)
                ).AndReturn( 'commitId' )
        mockRepo.create_reference(
                self.CommitRefPrefix + self.NameToUse, 'commitId'
                ).AndReturn( 'reference' )

        self.mox.ReplayAll()

        s = self.TestClass( self.NameToUse, mockRepo )
        actual = s.Create(content='some content')
        self.assertEqual( 'reference', actual )
        self.mox.VerifyAll()

    def testAutoCreate(self):
        '''
        Testing content is automatically created if it doesn't exist
        '''
        self.mox.StubOutWithMock( self.TestClass, 'Create' )
        mockRepo = self.mox.CreateMock( pygit2.Repository )

        # Setup mocks for missing ref, and creation
        mockRepo.lookup_reference(
                self.CommitRefPrefix + self.NameToUse
                ).AndRaise( KeyError )
        self.TestClass.Create().AndReturn( TestObjectType( 'oid' ) )

        # Setup for getting the content
        mockRepo[ 'oid' ].AndReturn(
                TestCommitType( [TestObjectType( 'oid2' )], 'coid', [] )
                )
        mockRepo[ 'oid2' ].AndReturn( TestBlobType( 'data' ) )

        # Now, try it out
        self.mox.ReplayAll()
        s = self.TestClass( self.NameToUse, mockRepo, create=True )
        content = s.CurrentContent()
        self.mox.VerifyAll()
        self.assertEqual( 'data', content )

    def testMissingContent(self):
        '''
        Testing that Content throws when it can't be found
        '''
        if self.TestClass.AutoCreate:
            # No need to test AutoCreate classes
            return

        self.mox.StubOutWithMock( self.TestClass, 'Create' )
        mockRepo = self.mox.CreateMock( pygit2.Repository )

        mockRepo.lookup_reference(
                self.CommitRefPrefix + self.NameToUse
                ).AndRaise( KeyError )

        self.mox.ReplayAll()
        s = self.TestClass( self.NameToUse, mockRepo )

        self.assertRaises( ContentNotFound, lambda: s.CurrentContent() )

    def testCurrentContent( self ):
        '''
        Testing db.Content.CurrentContent
        '''
        mockRepo, mockHead = self.setupRepoForGetHeadCommit()

        mockObject = TestObjectType( 'blobOid' )

        mockHead.tree = self.mox.CreateMockAnything()

        mockHead.tree[ 0 ].AndReturn( mockObject )

        mockBlob = TestBlobType( 'blobData' )

        mockRepo[ 'blobOid' ].AndReturn( mockBlob )

        self.mox.ReplayAll()

        s = self.TestClass( self.NameToUse, mockRepo )
        c = s.CurrentContent()

        self.mox.VerifyAll()
        self.assertEqual( 'blobData', c )

    def testSetContent( self ):
        '''
        Testing db.Content.SetContent
        '''
        mockRepo, mockHead = self.setupRepoForGetHeadCommit()

        gitutils.CommitBlob(
                mockRepo, 'content', self.NameToUse, 'Updating content',
                [ mockHead ], self.CommitRefPrefix + self.NameToUse
                ).AndReturn( 'newId' )

        mockRepo[ 'newId' ].AndReturn( 'newCommit' )

        self.mox.ReplayAll()

        s = self.TestClass( self.NameToUse, mockRepo )
        s.SetContent( 'content' )

        self.mox.VerifyAll()

    def testContentHistory(self):
        '''
        Testing db.Content.ContentHistory
        '''
        mockRepo, mockHead = self.setupRepoForGetHeadCommit()

        objects = [
                TestObjectType('oid1'),
                TestObjectType('oid2'),
                TestObjectType('oid3')
                ]
        secondParent = TestCommitType([objects[2]], '2ndParentOid', [])
        firstParent = TestCommitType(
                [objects[1]], '1stParentOid', [secondParent]
                )
        mockHead.tree = [objects[0]]
        mockHead.parents = [firstParent]

        expected = ['headData', '1stParentData', '2ndParentData']
        mockRepo['oid1'].AndReturn(TestBlobType(expected[0]))
        mockRepo['oid2'].AndReturn(TestBlobType(expected[1]))
        mockRepo['oid3'].AndReturn(TestBlobType(expected[2]))

        self.mox.ReplayAll()

        s = self.TestClass(self.NameToUse, mockRepo)
        history = s.ContentHistory()
        self.assertEqual( expected, list(history))
