
import json
import flask.ext.should_dsl
from should_dsl import should
from .base import BaseTest
from db import Document, Stylesheet
from views.api import stylesheet

# Keep pyflakes happy
return_200 = be_200 = abort_400 = have_json = None
flask.ext.should_dsl


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

        self.mox.ReplayAll()
        response = self.client.get( '/api/stylesheet' )
        response |should| be_200
        response |should| have_json(content=cssContent)
        self.mox.VerifyAll()


class TestGetStylesheetHistory(BaseStylesheetTest):
    def should_get_stylesheet_history(self):
        style = self.mox.CreateMock( Stylesheet )
        self.doc.GetStylesheet().AndReturn( style )

        contentHistory = [ 'one', 'two', 'three' ]
        style.ContentHistory().AndReturn( contentHistory )

        self.mox.ReplayAll()
        response = self.client.get( '/api/stylesheet/history' )
        response |should| be_200
        response |should| have_json([{ 'content': c } for c in contentHistory])
        self.mox.VerifyAll()


class TestSetStylesheetContent(BaseStylesheetTest):
    def should_set_stylesheet_content(self):
        style = self.mox.CreateMock( Stylesheet )
        self.doc.GetStylesheet().AndReturn( style )

        style.CurrentContent().AndReturn( '' )
        style.SetContent( 'xyzz' )

        inputStruct = { 'content': 'xyzz' }

        self.mox.ReplayAll()
        self.client.put(
                '/api/stylesheet',
                data=json.dumps(inputStruct),
                content_type='application/json',
                ) |should| return_200
        self.mox.VerifyAll()

    def should_ignore_if_no_change(self):
        style = self.mox.CreateMock( Stylesheet )
        self.doc.GetStylesheet().AndReturn( style )

        style.CurrentContent().AndReturn( 'xyzz' )

        inputStruct = { 'content': 'xyzz' }

        self.mox.ReplayAll()
        self.client.put(
                '/api/stylesheet',
                data=json.dumps(inputStruct),
                content_type='application/json',
                ) |should| return_200
        self.mox.VerifyAll()

    def should_error_on_missing_content(self):
        style = self.mox.CreateMock( Stylesheet )
        self.doc.GetStylesheet().AndReturn( style )

        inputStruct = { 'somethingElse': 'xyzz' }

        self.mox.ReplayAll()
        with self.assertRaises(KeyError):
            self.client.put(
                    '/api/stylesheet',
                    data=json.dumps(inputStruct),
                    content_type='application/json',
                    )
        self.mox.VerifyAll()

    def should_error_if_stylesheet_too_big(self):
        style = self.mox.CreateMock( Stylesheet )
        self.doc.GetStylesheet().AndReturn( style )

        inputStruct = {'content': 'x' * (1024*513)}

        self.mox.ReplayAll()
        self.client.put(
                '/api/stylesheet',
                data=json.dumps(inputStruct),
                content_type='application/json',
                ) |should| abort_400
        self.mox.VerifyAll()
