
import resumr
import json
import unittest
import mox
from StringIO import StringIO
from db import Section, Document, SectionNotFound, RepoNotFound, Stylesheet
from services import OAuthException
from services.auth import BaseOAuth2
from services.facebook import FacebookService
from flaskext.testing import TestCase
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

    def testIsLoggedIn(self):
        with resumr.app.test_request_context('/'):
            resumr.app.preprocess_request()
            session.new = False
            session[ 'email' ] = 'something'
            assert resumr.IsLoggedIn()

    def testNotLoggedIn(self):
        with resumr.app.test_request_context('/'):
            resumr.app.preprocess_request()
            assert not resumr.IsLoggedIn()

    def testGetDocLoggedIn(self):
        self.mox.StubOutClassWithMocks(resumr, 'Document')
        d = resumr.Document( 'facebook - something', rootPath=None )

        self.mox.ReplayAll()
        with resumr.app.test_request_context('/'):
            resumr.app.preprocess_request()
            session.new = False
            session[ 'email' ] = 'something'
            session[ 'regType' ] = 'facebook'
            self.assertIs( resumr.GetDoc(), d )
        self.mox.VerifyAll()

    def testGetDocWithRootPath(self):
        self.mox.StubOutClassWithMocks(resumr, 'Document')
        d = resumr.Document( 'facebook - something', rootPath='somewhere' )

        self.mox.ReplayAll()
        try:
            resumr.app.config[ 'DATA_PATH' ] = 'somewhere'
            with resumr.app.test_request_context('/'):
                resumr.app.preprocess_request()
                session.new = False
                session[ 'email' ] = 'something'
                session[ 'regType' ] = 'facebook'
                self.assertIs( resumr.GetDoc(), d )
            self.mox.VerifyAll()
        finally:
            resumr.app.config[ 'DATA_PATH' ] = None

    def testGetDocNotLoggedIn(self):
        self.mox.StubOutWithMock(resumr, 'IsLoggedIn')
        self.mox.StubOutWithMock(resumr, 'abort')
        resumr.IsLoggedIn().AndReturn( False )
        resumr.abort( 401 ).AndRaise( Exception )

        self.mox.ReplayAll()
        with self.assertRaises( Exception ):
            resumr.GetDoc()
        self.mox.VerifyAll()

    def testGetDocMissingKeys(self):
        self.mox.StubOutWithMock(resumr, 'IsLoggedIn')
        self.mox.StubOutWithMock(resumr, 'abort')
        resumr.IsLoggedIn().AndReturn( True )
        resumr.abort( 401 ).AndRaise( Exception )

        self.mox.ReplayAll()
        with resumr.app.test_request_context('/'):
            resumr.app.preprocess_request()
            with self.assertRaises( Exception ):
                resumr.GetDoc()
        self.mox.VerifyAll()

    def testGetDocCreateRequired(self):
        self.mox.StubOutWithMock(resumr, 'Document' )
        resumr.Document(
                'facebook - something', rootPath=None
                ).AndRaise( RepoNotFound )
        resumr.Document(
                'facebook - something', create=True, rootPath=None
                ).AndReturn( 'document')

        self.mox.ReplayAll()
        with resumr.app.test_request_context('/'):
            resumr.app.preprocess_request()
            session.new = False
            session[ 'email' ] = 'something'
            session[ 'regType' ] = 'facebook'
            self.assertEqual( resumr.GetDoc(), 'document' )
        self.mox.VerifyAll()

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

    def testListSections(self):
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        # First create some mock sections
        sectionList = []
        for i in range( 100 ):
            s = self.mox.CreateMock( Section )
            s.name = str( i )
            sectionList.append( ( i, s ) )

        # Return the mock sections from CurrentSections()
        doc.CurrentSections().AndReturn( sectionList )

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
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        s = self.mox.CreateMock( Section )
        s.name = 'wierdly'
        doc.FindSection( 'wierdly' ).AndReturn( s )
        s.GetPosition().AndReturn( 512 )
        s.CurrentContent().AndReturn( 'some content' )

        expected = { 'name': 'wierdly', 'pos': 512, 'content': 'some content' }

        self.mox.ReplayAll()
        rv = self.client.get( '/api/sections/wierdly' )
        self.mox.VerifyAll()
        self.assert200( rv )
        self.assertEqual( expected, rv.json )

    def testGetMissingSection(self):
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        doc.FindSection( 'missing' ).AndRaise( SectionNotFound )

        self.mox.ReplayAll()
        rv = self.client.get( '/api/sections/missing' )
        self.mox.VerifyAll()
        self.assert404( rv )

    def testAddSection(self):
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        inputStruct = { 'newName': 'alfred', 'content': 'woot' }
        inputStr = json.dumps( inputStruct )
        inputStream = StringIO( inputStr )

        s = self.mox.CreateMock( Section )
        doc.AddSection( 'alfred', 'woot' ).AndReturn( s )
        s.name = 'jones'
        s.GetPosition().AndReturn( 100 )

        self.mox.ReplayAll()

        expected = { 'name': 'jones', 'content': 'woot', 'pos': 100 }

        rv = self.client.post(
                '/api/sections',
                input_stream=inputStream,
                content_type='application/json',
                content_length=len(inputStr)
                )
        self.mox.VerifyAll()
        self.assert200( rv )
        self.assertEqual( expected, rv.json )

    def testUpdateSection(self):
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        inputStruct = { 'pos': 500, 'content': 'woot' }
        inputStr = json.dumps( inputStruct )
        inputStream = StringIO( inputStr )

        s = self.mox.CreateMock( Section )
        doc.FindSection( 'alfred' ).AndReturn( s )
        s.CurrentContent().AndReturn( 'notthesame' )
        s.SetContent( 'woot' )
        s.GetPosition().AndReturn( 100 )
        s.SetPosition( 500 )

        self.mox.ReplayAll()
        rv = self.client.put(
                '/api/sections/alfred',
                input_stream=inputStream,
                content_type='application/json',
                content_length=len(inputStr)
                )
        self.mox.VerifyAll()
        self.assert200( rv )
        # TODO: Might want to verify the content returned as well

    def testUpdateMissingSection(self):
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        inputStruct = { 'pos': 500, 'content': 'woot' }
        inputStr = json.dumps( inputStruct )
        inputStream = StringIO( inputStr )

        doc.FindSection( 'jenga' ).AndRaise( SectionNotFound )

        self.mox.ReplayAll()
        rv = self.client.put(
                '/api/sections/jenga',
                input_stream=inputStream,
                content_type='application/json',
                content_length=len(inputStr)
                )
        self.mox.VerifyAll()
        self.assert404( rv )

    def testUpdateSectionPosition(self):
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        inputStruct = { 'pos': 500, 'content': 'woot' }
        inputStr = json.dumps( inputStruct )
        inputStream = StringIO( inputStr )

        s = self.mox.CreateMock( Section )
        doc.FindSection( 'alfred' ).AndReturn( s )
        s.CurrentContent().AndReturn( 'woot' )
        s.GetPosition().AndReturn( 100 )
        s.SetPosition( 500 )

        self.mox.ReplayAll()
        rv = self.client.put(
                '/api/sections/alfred',
                input_stream=inputStream,
                content_type='application/json',
                content_length=len(inputStr)
                )
        self.mox.VerifyAll()
        self.assert200( rv )

    def testUpdateSectionContent(self):
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        inputStruct = { 'pos': 500, 'content': 'woot' }
        inputStr = json.dumps( inputStruct )
        inputStream = StringIO( inputStr )

        s = self.mox.CreateMock( Section )
        doc.FindSection( 'alfred' ).AndReturn( s )
        s.CurrentContent().AndReturn( 'notthesame' )
        s.SetContent( 'woot' )
        s.GetPosition().AndReturn( 500 )

        self.mox.ReplayAll()
        rv = self.client.put(
                '/api/sections/alfred',
                input_stream=inputStream,
                content_type='application/json',
                content_length=len(inputStr)
                )
        self.mox.VerifyAll()
        self.assert200( rv )

    def testRemoveSection(self):
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        doc.RemoveSection( 'jenkins' )
        self.mox.ReplayAll()

        rv = self.client.delete( '/api/sections/jenkins' )
        self.mox.VerifyAll()
        self.assert200( rv )

    def testSectionHistory(self):
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        s = self.mox.CreateMock( Section )
        doc.FindSection( 'charlie' ).AndReturn( s )

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
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        doc.FindSection( 'charlie' ).AndRaise( SectionNotFound )

        self.mox.ReplayAll()
        rv = self.client.get( '/api/sections/charlie/history' )
        self.mox.VerifyAll()
        self.assert404( rv )

    def testSelectSectionHistory(self):
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        s = self.mox.CreateMock( Section )
        doc.FindSection( 'zordon' ).AndReturn( s )

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
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        doc.FindSection( 'zordon' ).AndRaise( SectionNotFound )

        self.mox.ReplayAll()
        rv = self.client.post( '/api/sections/zordon/history/select/35' )
        self.mox.VerifyAll()
        self.assert404( rv )

    def testSelectSectionHistoryInvalidId(self):
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        s = self.mox.CreateMock( Section )
        doc.FindSection( 'zordon' ).AndReturn( s )

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

    def testRender(self):
        self.mox.StubOutWithMock( resumr, 'IsLoggedIn' )
        self.mox.StubOutWithMock( resumr.markdown, 'markdown' )
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
            contentStr = 'content' + str(i)
            markdownStr = 'markdown' + str(i)
            s.CurrentContent().AndReturn( contentStr )
            resumr.markdown.markdown(
                    contentStr
                    ).AndReturn( markdownStr )
            expected.append( markdownStr )

        self.mox.ReplayAll()
        rv = self.client.get( '/render' )
        self.assert200( rv )
        self.assertTemplateUsed( 'render.html' )
        self.assertContext( 'sections', expected )

        # Check that the output contains all the expected text
        for text in expected:
            self.assertIn( text, rv.data )

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
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        style = self.mox.CreateMock( Stylesheet )
        doc.GetStylesheet().AndReturn( style )

        cssContent = 'h1 { text-align: test; }'
        style.CurrentContent().AndReturn( cssContent )

        expected = json.dumps({ 'content': cssContent })

        self.mox.ReplayAll()
        rv = self.client.get( '/stylesheet' )
        self.mox.VerifyAll()
        self.assertStatus(rv, 200)
        self.assertEqual( expected, rv.json )

    def testGetStylesheetHistory(self):
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        style = self.mox.CreateMock( Stylesheet )
        doc.GetStylesheet().AndReturn( style )

        contentHistory = [ 'one', 'two', 'three' ]
        style.ContentHistory().AndReturn( contentHistory )

        expected = json.dumps([{ 'content': c } for c in contentHistory])

        self.mox.ReplayAll()
        rv = self.client.get( '/stylesheet/history' )
        self.mox.VerifyAll()
        self.assertStatus(rv, 200)
        self.assertEqual( expected, rv.json )

    def testSetStylesheetContent(self):
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        style = self.mox.CreateMock( Stylesheet )
        doc.GetStylesheet().AndReturn( style )

        style.SetContent( 'xyzz' )

        inputStruct = { 'content': 'xyzz' }
        inputStr = json.dumps( inputStruct )
        inputStream = StringIO( inputStr )

        self.mox.ReplayAll()
        rv = self.client.put(
                '/stylesheet',
                input_stream=inputStream,
                content_type='application/json',
                content_length=len(inputStr)
                )
        self.mox.VerifyAll()
        self.assertStatus(rv, 200)

if __name__ == "__main__":
    unittest.main()
