
import resumr
import unittest
import mox
from db import Section, Document, Stylesheet
from flask.ext.testing import TestCase


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


if __name__ == "__main__":
    unittest.main()
