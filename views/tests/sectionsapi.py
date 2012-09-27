
import mox
import resumr
import json
import flask.ext.should_dsl
from flask.ext.testing import TestCase
from should_dsl import should
from db import Section, Document
from db.errors import ContentNotFound
from views.api import sections

# Let's keep pyflakes happy
flask.ext.should_dsl
abort_500 = None


class TestSectionsApi(TestCase, mox.MoxTestBase):

    def create_app(self):
        resumr.app.config['SERVER_NAME'] = 'localhost:5000'
        resumr.app.config['SECRET_KEY'] = 'testsecret'
        resumr.app.config['TESTING'] = True
        resumr.app.config['BYPASS_LOGIN'] = False
        resumr.app.testing = True
        return resumr.app

    def setUp(self):
        super( TestSectionsApi, self ).setUp()
        self.mox.StubOutWithMock(sections, 'ValidateMarkdown')
        self.mox.StubOutWithMock(sections, 'GetDoc' )

        # Every test requires these at present
        self.doc = self.mox.CreateMock( Document )
        sections.GetDoc().AndReturn(self.doc)

    def tearDown(self):
        self.mox.UnsetStubs()

    def testListSections(self):
        # First create some mock sections
        sectionList = []
        for i in range( 100 ):
            s = self.mox.CreateMock( Section )
            s.name = str( i )
            sectionList.append( ( i, s ) )

        # Return the mock sections from CurrentSections()
        self.doc.CurrentSections().AndReturn( sectionList )

        # Set up the mock sections to return some content
        for i, s in sectionList:
            s.CurrentContent().AndReturn( 'Content' + str( i ) )

        self.mox.ReplayAll()

        # Build up our expected data
        expected = []
        for i in range( 100 ):
            thisRow = {
                    'name': str( i ),
                    'pos': i,
                    'content': 'Content' + str( i )
                    }
            expected.append( thisRow )

        rv = self.client.get('/api/sections')
        self.mox.VerifyAll()
        self.assert200( rv )
        self.assertEqual( expected, rv.json )

    def testGetSection(self):
        s = self.mox.CreateMock( Section )
        s.name = 'wierdly'
        self.doc.FindSection( 'wierdly' ).AndReturn( s )
        s.GetPosition().AndReturn( 512 )
        s.CurrentContent().AndReturn( 'some content' )

        expected = { 'name': 'wierdly', 'pos': 512, 'content': 'some content' }

        self.mox.ReplayAll()
        rv = self.client.get( '/api/sections/wierdly' )
        self.mox.VerifyAll()
        self.assert200( rv )
        self.assertEqual( expected, rv.json )

    def testGetMissingSection(self):
        self.doc.FindSection( 'missing' ).AndRaise( ContentNotFound )

        self.mox.ReplayAll()
        rv = self.client.get( '/api/sections/missing' )
        self.mox.VerifyAll()
        self.assert404( rv )

    def testAddSection(self):
        inputStruct = { 'newName': 'alfred', 'content': 'woot' }

        s = self.mox.CreateMock( Section )
        sections.ValidateMarkdown( 'woot' )
        self.doc.AddSection( 'alfred', 'woot' ).AndReturn( s )
        s.name = 'jones'
        s.GetPosition().AndReturn( 100 )

        self.mox.ReplayAll()

        expected = { 'name': 'jones', 'content': 'woot', 'pos': 100 }

        rv = self.client.post(
                '/api/sections',
                data=json.dumps(inputStruct),
                content_type='application/json',
                )
        self.mox.VerifyAll()
        self.assert200( rv )
        self.assertEqual( expected, rv.json )

    def doAddSectionFailTest(self, markdownFail=False, **inputStruct):
        ''' Utility function called by the add section fail tests '''
        if markdownFail:
            sections.ValidateMarkdown(
                    inputStruct['content']
                    ).AndRaise( sections.MarkdownValidationError )

        self.mox.ReplayAll()

        self.client.post(
                '/api/sections',
                data=json.dumps(inputStruct),
                content_type='application/json'
                ) |should| abort_500
        self.mox.VerifyAll()

    def testAddSectionEmptyName(self):
        ''' Testing adding a section with an empty name '''
        self.doAddSectionFailTest(newName='', content='woot')

    def testAddSectionNoName(self):
        ''' Testing adding a section with no name '''
        self.doAddSectionFailTest(content='woot')

    def testAddSectionNameWithSpaces(self):
        ''' Testing adding a section with a name with spaces '''
        self.doAddSectionFailTest(newName='some thing', content='woot')

    def testAddSectionNameWithNonWordChars(self):
        ''' Testing adding a section with non-word chars '''
        self.doAddSectionFailTest(newName='some&', content='woot')

    def testAddSectionNoContent(self):
        ''' Testing adding a section with no content '''
        self.doAddSectionFailTest(newName='some')

    def testAddSectionRejectedMarkdown(self):
        ''' Testing adding a section with rejected markdown '''
        self.doAddSectionFailTest(
                markdownFail=True, newName='some', content='x'
                )

    def testUpdateSection(self):
        inputStruct = { 'pos': 500, 'content': 'woot' }

        s = self.mox.CreateMock( Section )
        self.doc.FindSection( 'alfred' ).AndReturn( s )
        s.CurrentContent().AndReturn( 'notthesame' )
        sections.ValidateMarkdown('woot' )
        s.SetContent( 'woot' )
        s.GetPosition().AndReturn( 100 )
        s.SetPosition( 500 )

        self.mox.ReplayAll()
        rv = self.client.put(
                '/api/sections/alfred',
                data=json.dumps(inputStruct),
                content_type='application/json',
                )
        self.mox.VerifyAll()
        self.assert200( rv )
        # TODO: Might want to verify the content returned as well

    def testUpdateMissingSection(self):
        inputStruct = { 'pos': 500, 'content': 'woot' }

        self.doc.FindSection( 'jenga' ).AndRaise( ContentNotFound )

        self.mox.ReplayAll()
        rv = self.client.put(
                '/api/sections/jenga',
                data=json.dumps(inputStruct),
                content_type='application/json',
                )
        self.mox.VerifyAll()
        self.assert404( rv )

    def testUpdateSectionPosition(self):
        inputStruct = { 'pos': 500, 'content': 'woot' }

        s = self.mox.CreateMock( Section )
        self.doc.FindSection( 'alfred' ).AndReturn( s )
        s.CurrentContent().AndReturn( 'woot' )
        s.GetPosition().AndReturn( 100 )
        s.SetPosition( 500 )

        self.mox.ReplayAll()
        rv = self.client.put(
                '/api/sections/alfred',
                data=json.dumps(inputStruct),
                content_type='application/json',
                )
        self.mox.VerifyAll()
        self.assert200( rv )

    def testUpdateSectionContent(self):
        inputStruct = { 'pos': 500, 'content': 'woot' }

        s = self.mox.CreateMock( Section )
        self.doc.FindSection( 'alfred' ).AndReturn( s )
        s.CurrentContent().AndReturn( 'notthesame' )
        sections.ValidateMarkdown( 'woot' )
        s.SetContent( 'woot' )
        s.GetPosition().AndReturn( 500 )

        self.mox.ReplayAll()
        rv = self.client.put(
                '/api/sections/alfred',
                data=json.dumps(inputStruct),
                content_type='application/json',
                )
        self.mox.VerifyAll()
        self.assert200( rv )

    def testUpdateSectionContentValidateFail(self):
        ''' Testing validation failures when updating a section '''
        inputStruct = { 'pos': 500, 'content': 'woot' }

        s = self.mox.CreateMock( Section )
        self.doc.FindSection( 'alfred' ).AndReturn( s )
        s.CurrentContent().AndReturn( 'notthesame' )
        sections.ValidateMarkdown(
                'woot'
                ).AndRaise( sections.MarkdownValidationError )

        self.mox.ReplayAll()
        self.client.put(
                '/api/sections/alfred',
                data=json.dumps(inputStruct),
                content_type='application/json',
                ) |should| abort_500
        self.mox.VerifyAll()

    def testRemoveSection(self):
        self.doc.RemoveSection( 'jenkins' )
        self.mox.ReplayAll()

        rv = self.client.delete( '/api/sections/jenkins' )
        self.mox.VerifyAll()
        self.assert200( rv )

    def testSectionHistory(self):
        s = self.mox.CreateMock( Section )
        self.doc.FindSection( 'charlie' ).AndReturn( s )

        # Build a list of fake history
        history = []
        expected = []
        for i in range( 100 ):
            content = 'history' + str(i)
            history.append( content )
            expected.append({ 'id': i, 'content': content })
        s.ContentHistory().AndReturn( history )

        self.mox.ReplayAll()
        rv = self.client.get( '/api/sections/charlie/history' )
        self.mox.VerifyAll()
        self.assert200( rv )
        self.assertEqual( expected, rv.json )

    def testSectionHistoryMissingSection(self):
        self.doc.FindSection( 'charlie' ).AndRaise( ContentNotFound )

        self.mox.ReplayAll()
        rv = self.client.get( '/api/sections/charlie/history' )
        self.mox.VerifyAll()
        self.assert404( rv )

    def testSelectSectionHistory(self):
        s = self.mox.CreateMock( Section )
        self.doc.FindSection( 'zordon' ).AndReturn( s )

        # Build a list of fake history
        history = []
        for i in range( 100 ):
            content = 'history' + str(i)
            history.append( content )

        s.ContentHistory().AndReturn( history )
        s.SetContent( 'history35' )

        self.mox.ReplayAll()
        rv = self.client.post( '/api/sections/zordon/history/select/35' )
        self.mox.VerifyAll()
        self.assert200( rv )

    def testSelectSectionHistoryMissingSection(self):
        self.doc.FindSection( 'zordon' ).AndRaise( ContentNotFound )

        self.mox.ReplayAll()
        rv = self.client.post( '/api/sections/zordon/history/select/35' )
        self.mox.VerifyAll()
        self.assert404( rv )

    def testSelectSectionHistoryInvalidId(self):
        s = self.mox.CreateMock( Section )
        self.doc.FindSection( 'zordon' ).AndReturn( s )

        # Build a list of fake history
        history = []
        for i in range( 100 ):
            content = 'history' + str(i)
            history.append( content )

        s.ContentHistory().AndReturn( history )

        self.mox.ReplayAll()
        rv = self.client.post( '/api/sections/zordon/history/select/101' )
        self.mox.VerifyAll()
        self.assert404( rv )
