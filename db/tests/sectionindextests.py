
import pygit2
from .. import sectionindex
from ..constants import SECTION_INDEX_FILENAME, MASTER_REF
from .defs import BaseTest, TestCommitType, TestObjectType, TestBlobType
from .defs import StubOutConstructor


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
                'unused', []
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

    def testRemoveSection( self ):
        ''' Tests removing a section '''
        StubOutConstructor( self.mox, sectionindex.SectionIndex )
        sectionData = 'header\nfooter'

        self.mox.ReplayAll()

        headerIndexEntry = sectionindex.SectionIndexEntry( 'header' )

        index = sectionindex.SectionIndex()
        index.ProcessData( sectionData )

        # Remove the footer first
        index.RemoveSection( 'footer' )

        self.assertEqual( [ headerIndexEntry ], index.CurrentSections() )

        # Try to remove it again, shouldn't error
        index.RemoveSection( 'footer' )
        self.assertEqual( [ headerIndexEntry ], index.CurrentSections() )

        # Now remove the other section and check
        index.RemoveSection( 'header' )
        self.assertEqual( [], index.CurrentSections() )

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
                sectionindex.ContentNotFound,
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
                sectionindex.ContentNotFound,
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
