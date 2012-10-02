
import mox
from resumr import MakeApp
import json
from flask.ext.testing import TestCase
from db import Document, Stylesheet
from views.api import stylesheet


class TestStylesheetApi(TestCase, mox.MoxTestBase):

    def create_app(self):
        app = MakeApp()
        app.config['SERVER_NAME'] = 'localhost:5000'
        app.config['SECRET_KEY'] = 'testsecret'
        app.config['TESTING'] = True
        app.config['BYPASS_LOGIN'] = False
        app.testing = True
        return app

    def setUp(self):
        super( TestStylesheetApi, self ).setUp()
        self.mox.StubOutWithMock(stylesheet, 'GetDoc' )

        # Every test requires these at present
        self.doc = self.mox.CreateMock( Document )
        stylesheet.GetDoc().AndReturn(self.doc)

    def tearDown(self):
        self.mox.UnsetStubs()

    def testGetCurrentStylesheet(self):
        '''
        Testing the get current stylesheet API
        '''
        style = self.mox.CreateMock( Stylesheet )
        self.doc.GetStylesheet().AndReturn( style )

        cssContent = 'h1 { text-align: test; }'
        style.CurrentContent().AndReturn( cssContent )

        expected = { 'content': cssContent }

        self.mox.ReplayAll()
        rv = self.client.get( '/api/stylesheet' )
        self.mox.VerifyAll()
        self.assertStatus(rv, 200)
        self.assertEqual( expected, rv.json )

    def testGetStylesheetHistory(self):
        '''
        Testing the get stylesheet history API
        '''
        style = self.mox.CreateMock( Stylesheet )
        self.doc.GetStylesheet().AndReturn( style )

        contentHistory = [ 'one', 'two', 'three' ]
        style.ContentHistory().AndReturn( contentHistory )

        expected = [{ 'content': c } for c in contentHistory]

        self.mox.ReplayAll()
        rv = self.client.get( '/api/stylesheet/history' )
        self.mox.VerifyAll()
        self.assertStatus(rv, 200)
        self.assertEqual( expected, rv.json )

    def testSetStylesheetContent(self):
        '''
        Testing the set stylesheet content API
        '''
        style = self.mox.CreateMock( Stylesheet )
        self.doc.GetStylesheet().AndReturn( style )

        style.CurrentContent().AndReturn( '' )
        style.SetContent( 'xyzz' )

        inputStruct = { 'content': 'xyzz' }

        self.mox.ReplayAll()
        rv = self.client.put(
                '/api/stylesheet',
                data=json.dumps(inputStruct),
                content_type='application/json',
                )
        self.mox.VerifyAll()
        self.assertStatus(rv, 200)

    def testSetStylesheetContentNoChange(self):
        '''
        Testing the set stylesheet content API ignores duplicate data
        '''
        style = self.mox.CreateMock( Stylesheet )
        self.doc.GetStylesheet().AndReturn( style )

        style.CurrentContent().AndReturn( 'xyzz' )

        inputStruct = { 'content': 'xyzz' }

        self.mox.ReplayAll()
        rv = self.client.put(
                '/api/stylesheet',
                data=json.dumps(inputStruct),
                content_type='application/json',
                )
        self.mox.VerifyAll()
        self.assertStatus(rv, 200)

    def testSetStylesheetMissingContent(self):
        '''
        Testing the set stylesheet content API w/out content
        '''
        style = self.mox.CreateMock( Stylesheet )
        self.doc.GetStylesheet().AndReturn( style )

        inputStruct = { 'somethingElse': 'xyzz' }

        self.mox.ReplayAll()
        rv = self.client.put(
                '/api/stylesheet',
                data=json.dumps(inputStruct),
                content_type='application/json',
                )
        self.mox.VerifyAll()
        self.assertStatus(rv, 500)

    def testSetStylesheetTooBig(self):
        '''
        Testing the set stylesheet content API rejects large stylesheets
        '''
        style = self.mox.CreateMock( Stylesheet )
        self.doc.GetStylesheet().AndReturn( style )

        inputStruct = {'content': 'x' * (1024*513)}

        self.mox.ReplayAll()
        rv = self.client.put(
                '/api/stylesheet',
                data=json.dumps(inputStruct),
                content_type='application/json',
                )
        self.mox.VerifyAll()
        self.assertStatus(rv, 500)
