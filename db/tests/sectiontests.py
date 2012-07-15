
from content import ContentTests
from .. import section
from .defs import BaseTest


class SectionTests(ContentTests):
    '''
    Tests the section class

    Currently this only tests the
    CurrentContent & SetContent functions

    TODO: Write the rest of the tests
    '''
    TestClassType = section.Section

    def setUp( self ):
        super( SectionTests, self ).setUp()
        self.mox.StubOutWithMock(section, 'CommitBlob')

    def testGetPosition( self ):
        '''
        Testing the GetPosition function of a Section
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
        Testing the SetPosition function of a Section
        '''
        self.mox.StubOutClassWithMocks( section, 'SectionIndex' )
        mockIndex = section.SectionIndex( 'repo' )

        mockIndex.SetSectionPosition( 'sectionName', 100 )
        mockIndex.Save( 'repo' )
        self.mox.ReplayAll()

        s = section.Section( 'sectionName', 'commit', 'repo' )

        s.SetPosition( 100 )

        self.mox.VerifyAll()



