
import resumr
import json
import unittest
import mox
from StringIO import StringIO
from db import Section, Document, Stylesheet
from services import OAuthException
from services.auth import BaseOAuth2
from services.facebook import FacebookService
from flask.ext.testing import TestCase
from flask import session


class ResumrTests(TestCase):

    def create_app(self):
        resumr.app.config['SERVER_NAME'] = 'localhost:5000'
        resumr.app.config['SECRET_KEY'] = 'testsecret'
        resumr.app.config['TESTING'] = True
        resumr.app.config['BYPASS_LOGIN'] = False
        resumr.app.testing = True
        return resumr.app

    def setUp(self):
        self.mox = mox.Mox()
        self.mox.StubOutWithMock(resumr.markdown, 'markdown')
        self.mox.StubOutWithMock(resumr, 'CleanMarkdownOutput')

    def tearDown(self):
        self.mox.UnsetStubs()

    def assertRedirects(self, response, location):
        """
        Checks if response is an HTTP redirect to the
        given location.

        :param response: Flask response
        :param location: relative URL (i.e. without **http://localhost**)
        """
        self.assertTrue(response.status_code in (301, 302, 303))
        self.assertEqual(response.location, "http://localhost:5000" + location)

    def assert500(self, response):
        '''
        Checks if the response is a 500 error

        :param response:    Flask response
        '''
        self.assertEqual(response.status_code, 500)

    def testIndex(self):
        self.mox.StubOutWithMock(resumr, 'IsLoggedIn')
        resumr.IsLoggedIn().AndReturn( True )
        self.mox.ReplayAll()
        rv = self.client.get('/')
        self.mox.VerifyAll()
        self.assert200( rv )
        self.assertTemplateUsed( 'index.html' )

    def testIndexNotLoggedIn(self):
        self.mox.StubOutWithMock(resumr, 'IsLoggedIn')
        resumr.IsLoggedIn().AndReturn( False )
        self.mox.ReplayAll()
        rv = self.client.get('/')
        self.mox.VerifyAll()
        self.assertRedirects( rv, '/login' )

    def testRender(self):
        self.mox.StubOutWithMock( resumr, 'IsLoggedIn' )
        self.mox.StubOutWithMock( resumr, 'GetDoc' )

        resumr.IsLoggedIn().AndReturn( True )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        sections = [
                ( i, self.mox.CreateMock( Section ) ) for i in range( 100 )
                ]

        doc.CurrentSections().AndReturn( sections )

        expected = []
        for i, s in sections:
            s.name = '%i' % i
            contentStr = 'content' + str(i)
            s.CurrentContent().AndReturn(contentStr)

        for i, s in sections:
            contentStr = 'content' + str(i)
            markdownStr = 'markdown' + str(i)
            cleanStr = 'clean' + str(i)
            resumr.markdown.markdown(
                    contentStr
                    ).AndReturn( markdownStr )
            resumr.CleanMarkdownOutput(
                    markdownStr
                    ).AndReturn(cleanStr)
            expected.append(dict(name='%i' % i, content=cleanStr))

        mockStylesheet = self.mox.CreateMock( Stylesheet )
        doc.GetStylesheet().AndReturn( mockStylesheet )
        mockStylesheet.CurrentContent().AndReturn('h3 {}')

        self.mox.ReplayAll()
        rv = self.client.get( '/render' )
        self.assert200( rv )
        self.assertTemplateUsed( 'render.html' )
        self.assertContext( 'sections', expected )
        self.assertContext( 'stylesheet', 'h3 {}' )

        # Check that the output contains all the expected text
        for text in expected:
            self.assertIn( text['content'], rv.data )
        self.assertIn( 'h3 {}', rv.data )

    def testRenderNotLoggedIn(self):
        self.mox.StubOutWithMock( resumr, 'IsLoggedIn' )
        resumr.IsLoggedIn().AndReturn( False )

        self.mox.ReplayAll()
        rv = self.client.get( '/render' )
        self.mox.VerifyAll()
        self.assertRedirects( rv, '/login' )

    def testLogin(self):
        self.mox.StubOutWithMock( resumr, 'IsLoggedIn' )
        resumr.IsLoggedIn().AndReturn( False )
        self.mox.ReplayAll()
        rv = self.client.get( '/login' )
        self.mox.VerifyAll()
        self.assert200( rv )
        self.assertTemplateUsed( 'login.html' )

    def testLoginAlready(self):
        self.mox.StubOutWithMock( resumr, 'IsLoggedIn' )
        resumr.IsLoggedIn().AndReturn( True )
        self.mox.ReplayAll()
        rv = self.client.get( '/login' )
        self.mox.VerifyAll()
        self.assertRedirects( rv, '/' )

    def testOAuthCallback(self):
        self.mox.StubOutWithMock( resumr, 'GetAuthService' )
        authService = self.mox.CreateMock( BaseOAuth2 )
        service = self.mox.CreateMock( FacebookService )

        resumr.GetAuthService( 'facebook' ).AndReturn( authService )
        authService.ProcessAuthResponse( 'auth_code' ).AndReturn( service )
        service.GetUserEmail().AndReturn( 'someone@somewhere' )

        self.mox.ReplayAll()
        with self.client as client:
            rv = client.get(
                    '/login/auth/facebook',
                    query_string={ 'code': 'auth_code' }
                    )
            self.assertEqual( 'someone@somewhere', session[ 'email' ] )
        self.mox.VerifyAll()
        self.assertRedirects( rv, '/' )

    def testOAuthError(self):
        self.mox.ReplayAll()
        rv = self.client.get(
                '/login/auth/facebook',
                query_string={ 'error': 'e' }
                )
        self.mox.VerifyAll()
        self.assertStatus(rv, 500)

    def testOAuthException(self):
        self.mox.StubOutWithMock( resumr, 'GetAuthService' )
        authService = self.mox.CreateMock( BaseOAuth2 )
        self.mox.CreateMock( FacebookService )

        resumr.GetAuthService( 'facebook' ).AndReturn( authService )
        authService.ProcessAuthResponse( 'auth_code' ).AndRaise(
                OAuthException
                )

        self.mox.ReplayAll()
        rv = self.client.get(
                '/login/auth/facebook',
                query_string={ 'code': 'auth_code' }
                )
        self.mox.VerifyAll()
        self.assertStatus(rv, 500)

    def testOAuthNoCodeParam(self):
        self.mox.StubOutWithMock( resumr, 'GetAuthService' )
        authService = self.mox.CreateMock( BaseOAuth2 )
        self.mox.CreateMock( FacebookService )

        resumr.GetAuthService( 'facebook' ).AndReturn( authService )

        self.mox.ReplayAll()
        rv = self.client.get(
                '/login/auth/facebook',
                query_string={ 'something': 'auth_code' }
                )
        self.mox.VerifyAll()
        self.assertStatus(rv, 500)

    def testSystemTestReset(self):
        self.mox.StubOutWithMock( resumr.app, 'SystemTestReset' )

        resumr.app.SystemTestReset()

        self.mox.ReplayAll()
        try:
            resumr.app.config[ 'SYSTEM_TEST' ] = True
            rv = self.client.get( '/systemtest/reset' )
            self.mox.VerifyAll()
            self.assertStatus(rv, 200)
        finally:
            resumr.app.config[ 'SYSTEM_TEST' ] = False

    def testSystemTestLogout(self):
        try:
            resumr.app.config[ 'SYSTEM_TEST' ] = True
            resumr.app.config[ 'BYPASS_LOGIN' ] = True
            rv = self.client.get( '/systemtest/logout' )
            self.assertStatus(rv, 200)
            self.assertEqual( resumr.app.config[ 'BYPASS_LOGIN' ], False )
        finally:
            resumr.app.config[ 'SYSTEM_TEST' ] = False
            resumr.app.config[ 'BYPASS_LOGIN' ] = False

    def testSystemTestFail(self):
        systemTestUrls = (
                '/systemtest/reset', 'systemtest/logout'
                )
        for url in systemTestUrls:
            rv = self.client.get(url)
            self.assertStatus(rv, 403)

    def testGetCurrentStylesheet(self):
        '''
        Testing the get current stylesheet API
        '''
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        style = self.mox.CreateMock( Stylesheet )
        doc.GetStylesheet().AndReturn( style )

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
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        style = self.mox.CreateMock( Stylesheet )
        doc.GetStylesheet().AndReturn( style )

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
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        style = self.mox.CreateMock( Stylesheet )
        doc.GetStylesheet().AndReturn( style )

        style.CurrentContent().AndReturn( '' )
        style.SetContent( 'xyzz' )

        inputStruct = { 'content': 'xyzz' }
        inputStr = json.dumps( inputStruct )
        inputStream = StringIO( inputStr )

        self.mox.ReplayAll()
        rv = self.client.put(
                '/api/stylesheet',
                input_stream=inputStream,
                content_type='application/json',
                content_length=len(inputStr)
                )
        self.mox.VerifyAll()
        self.assertStatus(rv, 200)

    def testSetStylesheetContentNoChange(self):
        '''
        Testing the set stylesheet content API ignores duplicate data
        '''
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        style = self.mox.CreateMock( Stylesheet )
        doc.GetStylesheet().AndReturn( style )

        style.CurrentContent().AndReturn( 'xyzz' )

        inputStruct = { 'content': 'xyzz' }
        inputStr = json.dumps( inputStruct )
        inputStream = StringIO( inputStr )

        self.mox.ReplayAll()
        rv = self.client.put(
                '/api/stylesheet',
                input_stream=inputStream,
                content_type='application/json',
                content_length=len(inputStr)
                )
        self.mox.VerifyAll()
        self.assertStatus(rv, 200)

    def testSetStylesheetMissingContent(self):
        '''
        Testing the set stylesheet content API w/out content
        '''
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        style = self.mox.CreateMock( Stylesheet )
        doc.GetStylesheet().AndReturn( style )

        inputStruct = { 'somethingElse': 'xyzz' }
        inputStr = json.dumps( inputStruct )
        inputStream = StringIO( inputStr )

        self.mox.ReplayAll()
        rv = self.client.put(
                '/api/stylesheet',
                input_stream=inputStream,
                content_type='application/json',
                content_length=len(inputStr)
                )
        self.mox.VerifyAll()
        self.assertStatus(rv, 500)

    def testSetStylesheetTooBig(self):
        '''
        Testing the set stylesheet content API rejects large stylesheets
        '''
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        style = self.mox.CreateMock( Stylesheet )
        doc.GetStylesheet().AndReturn( style )

        inputStruct = {'content': 'x' * (1024*513)}

        self.mox.ReplayAll()
        rv = self.client.put(
                '/api/stylesheet',
                data=json.dumps(inputStruct),
                content_type='application/json',
                )
        self.mox.VerifyAll()
        self.assertStatus(rv, 500)


if __name__ == "__main__":
    unittest.main()
