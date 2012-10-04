
import json
from .base import BaseTest
from db import Document, Stylesheet
from views.api import stylesheet


class BaseStylesheetTest(BaseTest):

    def setUp(self):
        super( BaseStylesheetTest, self ).setUp()
        self.mox.StubOutWithMock(stylesheet, 'GetDoc' )

        # Every test requires these at present
        self.doc = self.mox.CreateMock( Document )
        stylesheet.GetDoc().AndReturn(self.doc)


class TestGetCurrentStylesheet(BaseStylesheetTest):

    def should_get_current_stylesheet(self):
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


class TestGetStylesheetHistory(BaseStylesheetTest):
    def should_get_stylesheet_history(self):
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


class TestSetStylesheetContent(BaseStylesheetTest):
    def should_set_stylesheet_content(self):
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

    def should_ignore_if_no_change(self):
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

    def should_error_on_missing_content(self):
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

    def should_error_if_stylesheet_too_big(self):
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
