
import mox
from resumr import MakeApp
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


class SectionApiTestBase(TestCase, mox.MoxTestBase):

    def create_app(self):
        app = MakeApp()
        app.config['SERVER_NAME'] = 'localhost:5000'
        app.config['SECRET_KEY'] = 'testsecret'
        app.config['TESTING'] = True
        app.config['BYPASS_LOGIN'] = False
        app.testing = True
        return app

    def setUp(self):
        super( SectionApiTestBase, self ).setUp()
        self.mox.StubOutWithMock(sections, 'ValidateMarkdown')
        self.mox.StubOutWithMock(sections, 'GetDoc' )

        # Every test requires these at present
        self.doc = self.mox.CreateMock( Document )
        sections.GetDoc().AndReturn(self.doc)

    def tearDown(self):
        self.mox.UnsetStubs()


class TestSectionList(SectionApiTestBase):

    def should_list_sections(self):
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


class TestGetSection(SectionApiTestBase):

    def should_get_a_section(self):
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

    def should_raise_404_on_missing(self):
        self.doc.FindSection( 'missing' ).AndRaise( ContentNotFound )

        self.mox.ReplayAll()
        rv = self.client.get( '/api/sections/missing' )
        self.mox.VerifyAll()
        self.assert404( rv )

class TestAddSection(SectionApiTestBase):

    def should_add_a_section(self):
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

    def should_fail_on_empty_name(self):
        self.doAddSectionFailTest(newName='', content='woot')

    def should_fail_on_no_name(self):
        self.doAddSectionFailTest(content='woot')

    def should_fail_if_name_has_spaces(self):
        self.doAddSectionFailTest(newName='some thing', content='woot')

    def should_fail_if_name_has_strange_characters(self):
        self.doAddSectionFailTest(newName='some&', content='woot')

    def should_fail_if_no_content(self):
        self.doAddSectionFailTest(newName='some')

    def should_fail_if_invalid_markdown(self):
        self.doAddSectionFailTest(
                markdownFail=True, newName='some', content='x'
                )


class TestUpdateSection(SectionApiTestBase):
    def should_update_section(self):
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

    def should_404_on_missing(self):
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

    def should_allow_position_only_updates(self):
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

    def should_allow_content_only_updates(self):
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

    def should_reject_invalid_content(self):
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


class TestRemoveSection(SectionApiTestBase):
    def should_remove_section(self):
        self.doc.RemoveSection( 'jenkins' )
        self.mox.ReplayAll()

        rv = self.client.delete( '/api/sections/jenkins' )
        self.mox.VerifyAll()
        self.assert200( rv )


class TestSectionHistoryList(SectionApiTestBase):
    def should_list_history(self):
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

    def should_404_on_missing(self):
        self.doc.FindSection( 'charlie' ).AndRaise( ContentNotFound )

        self.mox.ReplayAll()
        rv = self.client.get( '/api/sections/charlie/history' )
        self.mox.VerifyAll()
        self.assert404( rv )


class TestSelectSectionHistory(SectionApiTestBase):
    def should_select_section_history(self):
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

    def should_404_on_missing_section(self):
        self.doc.FindSection( 'zordon' ).AndRaise( ContentNotFound )

        self.mox.ReplayAll()
        rv = self.client.post( '/api/sections/zordon/history/select/35' )
        self.mox.VerifyAll()
        self.assert404( rv )

    def should_404_on_missing_history(self):
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
