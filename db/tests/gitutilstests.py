
import pygit2
from .. import gitutils
from .defs import BaseTest, TestCommitType


class GitUtilsTests(BaseTest):
    '''
    Tests for gitutils.py
    '''

    def testCommitBlob_Initial( self ):
        '''
        Tests committing initial blob
        '''
        self.doCommitTest( False, False )

    def testCommitBlob_Parents( self ):
        '''
        Tests committing blob with parents
        '''
        self.doCommitTest( True, False )

    def testCommitBlob_UpdateRef( self ):
        '''
        Tests committing blob with a ref to update
        '''
        self.doCommitTest( False, True )

    def testCommitBlob_ParentsAndUpdateRef( self ):
        '''
        Tests committing blob with parents & ref update
        '''
        self.doCommitTest( True, True )

    def doCommitTest( self, parents, updateRef ):
        '''
        Does a test of commit

        Args:
            parents     If true, supplies parent commits
            updateRef   If true, supplies an updateRef
        '''

        # Create some test constants
        signature = 'SignatureString'
        content = 'Some wonderous content'
        name = 'nameo'
        message = 'a brilliant message'
        testUpdateRef = 'something'
        parentCommits = [
                TestCommitType( 'tree0', 'oid0', [] ),
                TestCommitType( 'tree1', 'oid1', [] )
                ]

        # Mock out the time function
        self.mox.StubOutWithMock(gitutils.time, 'time' )
        gitutils.time.time().AndReturn( 100 )

        # Mock out the signature constructor
        self.mox.StubOutWithMock(gitutils.pygit2, 'Signature' )

        gitutils.pygit2.Signature(
                'Mr Name', 'name@domain.com', 100, 0
                ).AndReturn( signature )

        # Create the mock repo and set up it's expectations
        mockRepo = self.mox.CreateMock(pygit2.Repository)
        mockRepo.create_blob( content ).AndReturn( 'blob' )

        # Create the mock tree builder
        mockBuilder = self.mox.CreateMockAnything()

        if parents:
            mockRepo.TreeBuilder( 'tree0' ).AndReturn( mockBuilder )
        else:
            mockRepo.TreeBuilder().AndReturn( mockBuilder )

        mockBuilder.insert( name, 'blob', 0 )
        mockBuilder.write().AndReturn( 'treeOid' )

        mockRepo.create_commit(
                testUpdateRef if updateRef else None,
                signature, signature, message, 'treeOid',
                [ 'oid0', 'oid1' ] if parents else []
                ).AndReturn( 'commitId' )

        # Set up additional arguments for the test
        otherArgs = {}
        if parents:
            otherArgs[ 'parentCommits' ] = parentCommits
        if updateRef:
            otherArgs[ 'updateRef' ] = testUpdateRef

        # Go into replay mode, and run function
        self.mox.ReplayAll()

        commitId = gitutils.CommitBlob(
                mockRepo, content, name, message, **otherArgs
                )

        self.mox.VerifyAll()
        self.assertEqual( 'commitId', commitId )

