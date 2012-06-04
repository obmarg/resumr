
import os
import unittest
import mox
import pygit2
import gitutils
import doc
import section
import sectionindex
from constants import SECTION_INDEX_FILENAME, MASTER_REF
from collections import namedtuple


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()

TestBlobType = namedtuple( 'TestBlobType', [ 'data' ] )
TestCommitType = namedtuple( 'TestCommitType', [ 'tree', 'oid' ] )
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

        # Create some test constants
        signature = 'SignatureString'
        content = 'Some wonderous content'
        name = 'nameo'
        message = 'a brilliant message'
        testUpdateRef = 'something'
        parentCommits = [
                TestCommitType( 'tree0', 'oid0' ),
                TestCommitType( 'tree1', 'oid1' )
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

    def _createMockRepo( self ):
        '''
        Creates a mock repository for use in tests
        '''
        return doc.Repository(
                os.path.join( 'testPath', 'name.git' )
                )

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
                mockRepo, '', SECTION_INDEX_FILENAME, 'Initial commit'
                ).AndReturn( 'commitId' )
        mockRepo.create_reference( 'refs/heads/master', 'commitId' )

        # Now, run the test
        self.mox.ReplayAll()

        doc.Document( 'name', create=True )

        self.mox.VerifyAll()

    def testConstructNoCreate( self ):
        '''
        Tests construction without create
        '''
        self._createMockRepo()

        self.mox.ReplayAll()
        doc.Document( 'name' )

        self.mox.VerifyAll()

    def testNoRepo( self ):
        '''
        Tests that the correct exception is thrown
        if a repo doesn't exist
        '''
        self.mox.UnsetStubs()
        self.mox.StubOutWithMock(doc, 'Repository')

        doc.Repository(
                os.path.join( 'testPath', 'name.git' )
                ).AndRaise(KeyError)

        self.mox.ReplayAll()

        self.assertRaises(
                doc.RepoNotFound,
                lambda: doc.Document( 'name' )
                )

        self.mox.VerifyAll()

    def testAddSection( self ):
        '''
        Tests adding a section
        '''
        self.mox.StubOutClassWithMocks( doc, 'SectionIndex' )
        mockRepo = self._createMockRepo()

        doc.CommitBlob(
                mockRepo, 'content', 'sectionName',
                'Created section sectionName'
                ).AndReturn( 'commitId' )

        mockRef = TestObjectType( 'oid' )

        mockRepo.create_reference(
                'refs/heads/sections/sectionName',
                'commitId'
                ).AndReturn( mockRef )
        mockSectionIndex = doc.SectionIndex( mockRepo )
        mockSectionIndex.AddSection( 'sectionName' )
        mockSectionIndex.Save( mockRepo )
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
        mockRepo = self._createMockRepo()

        mockRef = TestObjectType( 'oid' )
        mockRef2 = TestObjectType( 'oid2' )

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

    def testFindSection( self ):
        '''
        Tests the find section function
        '''
        mockRepo = self._createMockRepo()

        mockRef = TestObjectType( 'oid' )

        mockRepo.lookup_reference(
                'refs/heads/sections/section'
                ).AndReturn( mockRef )

        mockRepo[ 'oid' ].AndReturn( 'commit' )

        mockSection = doc.Section( 'section', 'commit', mockRepo )

        self.mox.ReplayAll()

        d = doc.Document( 'name' )
        s = d.FindSection( 'section' )

        self.mox.VerifyAll()
        self.assertEqual( mockSection, s )

    def testFindMissingSection( self ):
        '''
        Tests finding a missing section
        '''
        mockRepo = self._createMockRepo()

        mockRepo.lookup_reference(
                'refs/heads/sections/section'
                ).AndRaise( KeyError )

        self.mox.ReplayAll()

        d = doc.Document( 'name' )

        self.assertRaises(
                doc.SectionNotFound,
                lambda: d.FindSection( 'section' )
                )

        self.mox.VerifyAll()

    def testCurrentSections( self ):
        '''
        Tests the current sections function
        '''
        mockRepo = self._createMockRepo()
        self.mox.StubOutClassWithMocks( doc, 'SectionIndex' )
        self.mox.StubOutWithMock(
                doc.Document,
                'FindSection'
                )

        EntryType = sectionindex.SectionIndexEntry
        sectionList = [
                EntryType( 'header' ),
                EntryType( 'body' ),
                EntryType( 'footer' )
                ]

        index = doc.SectionIndex( mockRepo )
        index.CurrentSections().AndReturn( sectionList )

        for s in sectionList:
            doc.Document.FindSection( s.name ).AndReturn( s )

        self.mox.ReplayAll()

        d = doc.Document( 'name' )

        result = d.CurrentSections()
        for expected, actual in zip( enumerate( sectionList ), result ):
            self.assertEqual( expected[0], actual[0] )
            self.assertEqual( expected[1], actual[1] )

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
        self.mox.StubOutWithMock(section, 'CommitBlob')

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

        s = section.Section( 'name', mockHead, mockRepo )
        c = s.CurrentContent()

        self.mox.VerifyAll()
        self.assertEqual( 'blobData', c )

    def testSetContent( self ):
        '''
        Tests the SetContent function
        '''
        mockHead = self.mox.CreateMock( pygit2.Commit )
        mockRepo = self.mox.CreateMock( pygit2.Repository )

        section.CommitBlob(
                mockRepo, 'content', 'name', 'Updating section',
                [ mockHead ], 'refs/heads/sections/name'
                ).AndReturn( 'newId' )

        mockRepo[ 'newId' ].AndReturn( 'newCommit' )

        self.mox.ReplayAll()

        s = section.Section( 'name', mockHead, mockRepo )
        s.SetContent( 'content' )

        self.mox.VerifyAll()
        self.assertEqual( s.headCommit, 'newCommit' )

    def testGetPosition( self ):
        '''
        Tests the GetPosition function
        '''
        self.mox.StubOutClassWithMocks( section, 'SectionIndex' )
        mockIndex = section.SectionIndex( 'repo' )

        mockIndex.GetSectionPosition( 'sectionName' ).AndReturn( 100 )
        self.mox.ReplayAll()

        s = section.Section( 'sectionName', 'commit', 'repo' )

        self.assertEqual( 100, s.GetPosition() )

        self.mox.VerifyAll()

    def testSetPosition( self ):
        '''
        Tests the SetPosition function
        '''
        self.mox.StubOutClassWithMocks( section, 'SectionIndex' )
        mockIndex = section.SectionIndex( 'repo' )

        mockIndex.SetSectionPosition( 'sectionName', 100 )
        mockIndex.Save( 'repo' )
        self.mox.ReplayAll()

        s = section.Section( 'sectionName', 'commit', 'repo' )

        s.SetPosition( 100 )

        self.mox.VerifyAll()


class SectionIndexTests(BaseTest):
    '''
    Tests the Section Index class
    '''

    def testConstruction( self ):
        '''
        Tests the construction of a SectionIndex
        '''

        # Set up our fake commit
        testCommit = TestCommitType(
                { SECTION_INDEX_FILENAME : TestObjectType( 'indexOid' ) },
                'unused'
                )
        testBlob = TestBlobType( 'someData' )

        mockRepo = self.mox.CreateMock( pygit2.Repository )
        self.mox.StubOutWithMock( sectionindex.SectionIndex, 'ProcessData' )

        mockRef = TestObjectType( 'mockOid' )
        mockRepo.lookup_reference( MASTER_REF ).AndReturn( mockRef )
        mockRepo[ 'mockOid' ].AndReturn( testCommit )
        mockRepo[ 'indexOid' ].AndReturn( testBlob )

        sectionindex.SectionIndex.ProcessData( testBlob.data )

        self.mox.ReplayAll()

        sectionindex.SectionIndex( mockRepo )

        self.mox.VerifyAll()

    def testProcessEmptyData( self ):
        '''
        Tests processing empty data
        '''
        StubOutConstructor( self.mox, sectionindex.SectionIndex )

        self.mox.StubOutWithMock( sectionindex, 'SectionIndexEntry' )
        self.mox.ReplayAll()

        sectionIndex = sectionindex.SectionIndex()
        sectionIndex.ProcessData( '' )

        self.mox.VerifyAll()
        self.assertEqual( [], sectionIndex.CurrentSections() )

    def testProcessAndCurrentSections( self ):
        '''
        Tests the process data function and that the correct result is returned
        from CurrentSections
        '''
        StubOutConstructor( self.mox, sectionindex.SectionIndex )

        self.mox.StubOutWithMock( sectionindex, 'SectionIndexEntry' )

        testData = 'header\nmiddle\nfooter'

        sectionindex.SectionIndexEntry( 'header' ).AndReturn( 'headerLine' )
        sectionindex.SectionIndexEntry( 'middle' ).AndReturn( 'middleLine' )
        sectionindex.SectionIndexEntry( 'footer' ).AndReturn( 'footerLine' )

        self.mox.ReplayAll()

        s = sectionindex.SectionIndex( None )
        s.ProcessData( testData )

        self.mox.VerifyAll()

        expectedData = [ 'headerLine', 'middleLine', 'footerLine' ]
        self.assertEqual( expectedData, s.CurrentSections() )

    def testAddSection( self ):
        ''' Tests add section '''
        StubOutConstructor( self.mox, sectionindex.SectionIndex )

        sectionData = 'header\nmiddle\nfooter'

        # Set up our section index
        index = sectionindex.SectionIndex()
        index.ProcessData( sectionData )

        self.mox.StubOutWithMock( sectionindex, 'SectionIndexEntry' )
        sectionindex.SectionIndexEntry( 'postFooter' ).AndReturn( 'string' )
        self.mox.ReplayAll()

        index.AddSection( 'postFooter' )
        sections = index.CurrentSections()
        self.assertEqual( 4, len( sections ) )
        self.assertEqual( 'string', sections[ 3 ] )

        self.mox.VerifyAll()

    def testGetSectionPosition( self ):
        '''
        Tests GetSectionPosition
        '''
        StubOutConstructor( self.mox, sectionindex.SectionIndex )

        sectionData = 'header\nmiddle\nfooter'

        # Set up our section index
        index = sectionindex.SectionIndex()
        index.ProcessData( sectionData )

        # Check we get the expected output
        self.assertEqual( 1, index.GetSectionPosition( 'middle' ) )
        self.assertEqual( 2, index.GetSectionPosition( 'footer' ) )
        self.assertEqual( 0, index.GetSectionPosition( 'header' ) )
        self.assertRaises(
                sectionindex.SectionNotFound,
                lambda: index.GetSectionPosition( 'missing' )
                )

    def testSetSectionPosition( self ):
        '''
        Tests SetSectionPosition
        '''

        def NumListToEntries( lst ):
            # Utility function to create Entry list
            return [
                    sectionindex.SectionIndexEntry( str( name ) )
                    for name in lst
                    ]

        StubOutConstructor( self.mox, sectionindex.SectionIndex )

        sectionData = '0\n1\n2\n3\n4'

        # Set up our section index
        index = sectionindex.SectionIndex()
        index.ProcessData( sectionData )

        # Now start testing.  First move zero to zero (a no-op)
        index.SetSectionPosition( '0', 0 )
        self.assertEqual(
                NumListToEntries( [ 0, 1, 2, 3, 4 ] ),
                index.CurrentSections()
                )

        # Now move 4 to 0
        index.SetSectionPosition( '4', 0 )
        self.assertEqual(
                NumListToEntries( [ 4, 0, 1, 2, 3 ] ),
                index.CurrentSections()
                )

        # Now move 0 to 3
        index.SetSectionPosition( '0', 3 )
        self.assertEqual(
                NumListToEntries( [ 4, 1, 2, 0, 3 ] ),
                index.CurrentSections()
                )

        # Now move 2 to 4
        index.SetSectionPosition( '2', 4 )
        self.assertEqual(
                NumListToEntries( [ 4, 1, 0, 3, 2 ] ),
                index.CurrentSections()
                )

        # Now test some too big/small numbers
        # Now move 4 to 10
        index.SetSectionPosition( '4', 10 )
        self.assertEqual(
                NumListToEntries( [ 1, 0, 3, 2, 4 ] ),
                index.CurrentSections()
                )

        # Check passing in negative numbers raises
        self.assertRaises(
                ValueError,
                lambda: index.SetSectionPosition( '1', -1 )
                )

        # Check section not found is raised
        self.assertRaises(
                sectionindex.SectionNotFound,
                lambda: index.SetSectionPosition( 'none', 10 )
                )

        # Check that our list is still the same as last time
        self.assertEqual(
                NumListToEntries( [ 1, 0, 3, 2, 4 ] ),
                index.CurrentSections()
                )

    def testSave( self ):
        StubOutConstructor( self.mox, sectionindex.SectionIndex )

        mockRepo = self.mox.CreateMock( pygit2.Repository )
        self.mox.StubOutWithMock( sectionindex, 'CommitBlob' )
        self.mox.StubOutWithMock( sectionindex.SectionIndex, 'GetIndexString' )

        sectionindex.SectionIndex.GetIndexString().AndReturn( 'indexString' )

        mockRef = TestObjectType( 'mockOid' )
        mockRepo.lookup_reference( MASTER_REF ).AndReturn( mockRef )
        mockRepo[ 'mockOid' ].AndReturn( 'commitObject' )

        sectionindex.CommitBlob(
                mockRepo,
                'indexString',
                SECTION_INDEX_FILENAME,
                'saving section index',
                [ 'commitObject' ],
                MASTER_REF
                )

        self.mox.ReplayAll()

        index = sectionindex.SectionIndex()
        index.Save( mockRepo )

        self.mox.VerifyAll()

    def testGetIndexString( self ):
        StubOutConstructor( self.mox, sectionindex.SectionIndex )

        index = sectionindex.SectionIndex()

        data = 'header\nmiddle\nfooter'

        index.ProcessData( data )

        self.assertEqual( data, index.GetIndexString() )
