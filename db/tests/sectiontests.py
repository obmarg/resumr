
import pygit2
from .. import section
from .defs import BaseTest, TestObjectType, TestBlobType


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



