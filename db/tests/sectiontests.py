
from content import ContentTests
from .. import section
from ..constants import SECTION_REF_PREFIX


class SectionTests(ContentTests):
    '''
    Tests the section class
    '''

    TestClass = section.Section
    CommitRefPrefix = SECTION_REF_PREFIX

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



