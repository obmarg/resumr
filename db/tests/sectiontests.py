
from content import ContentTests
from .. import section
from .. import gitutils
from ..constants import SECTION_REF_PREFIX


class SectionTests(ContentTests):
    '''
    Section Class Tests
    '''

    TestClass = section.Section
    CommitRefPrefix = SECTION_REF_PREFIX

    def setUp( self ):
        super( SectionTests, self ).setUp()

    def testGetPosition( self ):
        '''
        Testing db.Section.GetPosition
        '''
        self.mox.StubOutClassWithMocks( section, 'SectionIndex' )
        mockIndex = section.SectionIndex( 'repo' )

        mockIndex.GetSectionPosition( 'sectionName' ).AndReturn( 100 )
        self.mox.ReplayAll()

        s = section.Section( 'sectionName', 'repo' )

        self.assertEqual( 100, s.GetPosition() )

        self.mox.VerifyAll()

    def testSetPosition( self ):
        '''
        Testing db.Section.SetPosition
        '''
        self.mox.StubOutClassWithMocks( section, 'SectionIndex' )
        mockIndex = section.SectionIndex( 'repo' )

        mockIndex.SetSectionPosition( 'sectionName', 100 )
        mockIndex.Save( 'repo' )
        self.mox.ReplayAll()

        s = section.Section( 'sectionName', 'repo' )

        s.SetPosition( 100 )

        self.mox.VerifyAll()



