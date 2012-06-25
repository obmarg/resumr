
import os
import pygit2
from .. import doc
from .. import sectionindex
from ..constants import SECTION_INDEX_FILENAME
from .defs import BaseTest, TestObjectType


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
        self.origRootPath = doc.DEFAULT_ROOT_PATH
        doc.DEFAULT_ROOT_PATH = 'testPath'

    def tearDown( self ):
        super( DocumentTests, self ).tearDown()
        doc.DEFAULT_ROOT_PATH = self.origRootPath

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

    def testConstructWithRootPath( self ):
        '''
        Tests construction when we supply a root path
        '''
        testPath = os.path.join( '/', 'something', 'otherPath' )
        doc.Repository(
                os.path.join( testPath, 'name.git' )
                )

        self.mox.ReplayAll()
        doc.Document( 'name', rootPath=testPath )

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

    def testRemoveSection( self ):
        '''Tests removing a section'''
        self.mox.StubOutClassWithMocks( doc, 'SectionIndex' )
        mockRepo = self._createMockRepo()

        mockSectionIndex = doc.SectionIndex( mockRepo )
        mockSectionIndex.RemoveSection( 'sectionName' )
        mockSectionIndex.Save( mockRepo )

        self.mox.ReplayAll()

        d = doc.Document( 'name' )
        d.RemoveSection( 'sectionName' )

        self.mox.VerifyAll()

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



