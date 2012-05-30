
import os
import unittest
import mox
import pygit2
import gitutils
import doc
from collections import namedtuple

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()


class GitUtilsTest(BaseTest):
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

        commitTuple = namedtuple( 'commitTuple', [ 'tree', 'oid' ] )
        
        # Create some test constants
        signature = 'SignatureString'
        content = 'Some wonderous content'
        name = 'nameo'
        message = 'a brilliant message'
        testUpdateRef = 'something'
        parentCommits = [ 
                commitTuple( 'tree0', 'oid0' ), 
                commitTuple( 'tree1', 'oid1' ) 
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

class DocumentTests(BaseTest):
    '''
    Tests the document class
    '''

    def setUp( self ):
        super( DocumentTests, self ).setUp()
        self.mox.StubOutClassWithMocks(doc, 'Section')
        self.mox.StubOutClassWithMocks(doc, 'Repository')
        self.mox.StubOutWithMock(doc, 'init_repository')
        self.mox.StubOutWithMock(doc, 'CommitBlob')
        self.origRootPath = doc.rootPath
        doc.rootPath = 'testPath'

    def tearDown( self ):
        super( DocumentTests, self ).tearDown()
        doc.rootPath = self.origRootPath

    def testCreate( self ):
        '''
        Tests creation of document
        '''

        # Create a mock repo
        mockRepo = self.mox.CreateMock( pygit2.Repository )
        
        # Set up expectations.  First init repository
        doc.init_repository( 
                os.path.join( 'testPath', 'name.git' ), True
                ).AndReturn( mockRepo )
        # Then original commit & create master reference
        doc.CommitBlob( 
                mockRepo, '', 'layout', 'Initial commit'
                ).AndReturn( 'commitId' )
        mockRepo.create_reference( 'refs/heads/master', 'commitId' )

        # Now, run the test
        self.mox.ReplayAll()

        d = doc.Document( 'name', create=True )

        self.mox.VerifyAll()

    def testConstructNoCreate( self ):
        '''
        Tests construction without create
        '''

        mockRepo = doc.Repository( 
                os.path.join( 'testPath', 'name.git' )
                )

        self.mox.ReplayAll()
        d = doc.Document( 'name' )

        self.mox.VerifyAll()

    def testAddSection( self ):
        '''
        Tests adding a section
        '''

        mockRepo = doc.Repository( 
                os.path.join( 'testPath', 'name.git' )
                )

        doc.CommitBlob( 
                mockRepo, 'content', 'sectionName', 
                'Created section sectionName'
                ).AndReturn( 'commitId' )

        mockRefType = namedtuple( 'mockRef', 'oid' )
        mockRef = mockRefType( 'oid' )

        mockRepo.create_reference(
                'refs/heads/sections/sectionName',
                'commitId'
                ).AndReturn( mockRef )
        mockRepo[ 'oid' ].AndReturn( 'commit' )

        mockSection = doc.Section( 
                'sectionName', 'commit', mockRepo 
                )

        self.mox.ReplayAll()
        d = doc.Document( 'name' )

        s = d.AddSection( 'sectionName', 'content' )

        self.mox.VerifyAll()
        
        self.assertEqual( mockSection, s )

    def testListSections( self ):
        '''
        Tests the Sections function
        '''
        mockRepo = doc.Repository( 
                os.path.join( 'testPath', 'name.git' )
                )

        mockRefType = namedtuple( 'mockRef', 'oid' )
        mockRef = mockRefType( 'oid' )
        mockRef2 = mockRefType( 'oid2' )

        mockRepo.listall_references().AndReturn( [ 
            'refs/heads/sections/section',
            'refs/heads/sections/anotherSection',
            'refs/heads/master'
            ] )

        mockRepo.lookup_reference( 
                'refs/heads/sections/section' 
                ).AndReturn( mockRef )
        mockRepo[ 'oid' ].AndReturn( 'commit1' )
        mockSection1 = doc.Section( 'section', 'commit1', mockRepo )

        mockRepo.lookup_reference(
                'refs/heads/sections/anotherSection'
                ).AndReturn( mockRef2 )
        mockRepo[ 'oid2' ].AndReturn( 'commit2' )
        mockSection2 = doc.Section( 'anotherSection', 'commit2', mockRepo )

        self.mox.ReplayAll()

        d = doc.Document( 'name' )

        sections = list( d.Sections() )

        self.assertEqual( sections, [ mockSection1, mockSection2 ] )

        self.mox.VerifyAll()


class SectionTests(BaseTest):
    '''
    Tests the section class
   
    Currently this only tests the 
    CurrentContent & SetContent functions

    TODO: Write the rest of the tests
    '''

    def setUp( self ):
        super( SectionTests, self ).setUp()
        self.mox.StubOutWithMock(doc, 'CommitBlob')

    def testCurrentContent( self ):
        '''
        Tests the CurrentContent function
        '''
        mockHead = self.mox.CreateMock( pygit2.Commit )
        mockRepo = self.mox.CreateMock( pygit2.Repository )

        mockCommitType = namedtuple( 'mockTree', [ 'oid' ] )
        mockCommit = mockCommitType( 'blobOid' )

        mockHead.tree = self.mox.CreateMockAnything()

        mockHead.tree[ 0 ].AndReturn( mockCommit )
        
        mockBlobType = namedtuple( 'mockBlob', [ 'data' ] )
        mockBlob = mockBlobType( 'blobData' )

        mockRepo[ 'blobOid' ].AndReturn( mockBlob )

        self.mox.ReplayAll()

        section = doc.Section( 'name', mockHead, mockRepo )
        c =  section.CurrentContent()

        self.mox.VerifyAll()
        self.assertEqual( 'blobData', c )

    def testSetContent( self ):
        '''
        Tests the SetContent function
        '''
        mockHead = self.mox.CreateMock( pygit2.Commit )
        mockRepo = self.mox.CreateMock( pygit2.Repository )

        doc.CommitBlob(
                mockRepo, 'content', 'name', 'Updating section',
                [ mockHead ], 'refs/heads/sections/name'
                ).AndReturn( 'newId' )

        mockRepo[ 'newId' ].AndReturn( 'newCommit' )

        self.mox.ReplayAll()

        section = doc.Section( 'name', mockHead, mockRepo )
        section.SetContent( 'content' )

        self.mox.VerifyAll()
        self.assertEqual( section.headCommit, 'newCommit' )
 
