
import os
import pygit2
from .. import doc
from .. import sectionindex
from ..constants import SECTION_INDEX_FILENAME, STYLESHEET_REF_PREFIX
from .defs import BaseTest, TestObjectType


class DocumentTests(BaseTest):
    '''
    Tests the document class
    '''

    def setUp( self ):
        super( DocumentTests, self ).setUp()
        self.mox.StubOutClassWithMocks(doc, 'Section')
        self.mox.StubOutClassWithMocks(doc, 'Stylesheet')
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
        Testing db.Document constructor with create parameter
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
        Testing db.Document constructor without create parameter
        '''
        self._createMockRepo()

        self.mox.ReplayAll()
        doc.Document( 'name' )

        self.mox.VerifyAll()

    def testConstructWithRootPath( self ):
        '''
        Testing db.Document constructor with root path parameter
        '''
        testPath = os.path.join( '/', 'something', 'otherPath' )
        doc.Repository(
                os.path.join( testPath, 'name.git' )
                )

        self.mox.ReplayAll()
        doc.Document( 'name', rootPath=testPath )

    def testNoRepo( self ):
        '''
        Testing db.Document constructor when repo is missing
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
        Testing db.Document.AddSection
        '''
        self.mox.StubOutClassWithMocks( doc, 'SectionIndex' )
        mockRepo = self._createMockRepo()

        mockSection = doc.Section('sectionName', mockRepo, create=True)
        mockSection.Create(content='content')

        mockSectionIndex = doc.SectionIndex( mockRepo )
        mockSectionIndex.AddSection( 'sectionName' )
        mockSectionIndex.Save( mockRepo )

        self.mox.ReplayAll()
        d = doc.Document( 'name' )

        s = d.AddSection( 'sectionName', 'content' )

        self.mox.VerifyAll()

        self.assertEqual( mockSection, s )

    def testRemoveSection( self ):
        '''
        Testing db.Document.RemoveSection
        '''
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
        Testing db.Document.Sections
        '''
        mockRepo = self._createMockRepo()

        mockRepo.listall_references().AndReturn( [
            'refs/heads/sections/section',
            'refs/heads/sections/anotherSection',
            'refs/heads/master',
            'refs/heads/stylesheet',
            ] )

        mockSection1 = doc.Section( 'section', mockRepo )
        mockSection2 = doc.Section( 'anotherSection', mockRepo )

        self.mox.ReplayAll()

        d = doc.Document( 'name' )
        sections = list( d.Sections() )
        self.assertEqual( sections, [ mockSection1, mockSection2 ] )
        self.mox.VerifyAll()

    def testFindSection( self ):
        '''
        Testing db.Document.FindSection
        '''
        mockRepo = self._createMockRepo()

        mockSection = doc.Section( 'section', mockRepo )

        self.mox.ReplayAll()

        d = doc.Document( 'name' )
        s = d.FindSection( 'section' )

        self.mox.VerifyAll()
        self.assertEqual( mockSection, s )

    def testCurrentSections( self ):
        '''
        Testing db.Document.CurrentSections
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

    def testGetStylesheet(self):
        '''
        Testing db.Document.GetStylesheet
        '''
        mockRepo = self._createMockRepo()

        mockRef = TestObjectType( 'oid' )

        mockRepo.lookup_reference(
                STYLESHEET_REF_PREFIX
                ).AndReturn( mockRef )

        mockRepo[ 'oid' ].AndReturn( 'commit' )

        mockStylesheet = doc.Stylesheet( 'stylesheet', 'commit', mockRepo )

        self.mox.ReplayAll()

        d = doc.Document( 'name' )
        s = d.GetStylesheet()

        self.mox.VerifyAll()
        self.assertEqual( mockStylesheet, s )
