
import resumr
import unittest
import mox
from flask.ext.testing import TestCase


class ResumrTests(TestCase):

    def create_app(self):
        app = resumr.MakeApp()
        app.config['SERVER_NAME'] = 'localhost'
        app.config['SECRET_KEY'] = 'testsecret'
        app.config['TESTING'] = True
        app.config['BYPASS_LOGIN'] = False
        app.testing = True
        return app

    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()

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


if __name__ == "__main__":
    unittest.main()
