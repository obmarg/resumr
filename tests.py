
import resumr
import json
import unittest
import mox
from StringIO import StringIO
from db import Section, Document, ContentNotFound, Stylesheet
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
        self.mox.StubOutWithMock(resumr, 'ValidateMarkdown')
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

        doc.FindSection( 'missing' ).AndRaise( ContentNotFound )

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
        resumr.ValidateMarkdown( 'woot' )
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

    def doAddSectionFailTest(self, markdownFail=False, **inputStruct):
        ''' Utility function called by the add section fail tests '''
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        if markdownFail:
            resumr.ValidateMarkdown(
                    inputStruct['content']
                    ).AndRaise( resumr.MarkdownValidationError )

        self.mox.ReplayAll()

        rv = self.client.post(
                '/api/sections',
                data=json.dumps(inputStruct),
                content_type='application/json'
                )
        self.assert500(rv)

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
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        inputStruct = { 'pos': 500, 'content': 'woot' }
        inputStr = json.dumps( inputStruct )
        inputStream = StringIO( inputStr )

        s = self.mox.CreateMock( Section )
        doc.FindSection( 'alfred' ).AndReturn( s )
        s.CurrentContent().AndReturn( 'notthesame' )
        resumr.ValidateMarkdown('woot' )
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

        doc.FindSection( 'jenga' ).AndRaise( ContentNotFound )

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
        resumr.ValidateMarkdown( 'woot' )
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

    def testUpdateSectionContentValidateFail(self):
        ''' Testing validation failures when updating a section '''
        self.mox.StubOutWithMock( resumr, 'GetDoc' )
        doc = self.mox.CreateMock( Document )
        resumr.GetDoc().AndReturn( doc )

        inputStruct = { 'pos': 500, 'content': 'woot' }

        s = self.mox.CreateMock( Section )
        doc.FindSection( 'alfred' ).AndReturn( s )
        s.CurrentContent().AndReturn( 'notthesame' )
        resumr.ValidateMarkdown(
                'woot'
                ).AndRaise( resumr.MarkdownValidationError )

        self.mox.ReplayAll()
        rv = self.client.put(
                '/api/sections/alfred',
                data=json.dumps(inputStruct),
                content_type='application/json',
                )
        self.mox.VerifyAll()
        self.assert500( rv )

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

        doc.FindSection( 'charlie' ).AndRaise( ContentNotFound )

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

        doc.FindSection( 'zordon' ).AndRaise( ContentNotFound )

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
