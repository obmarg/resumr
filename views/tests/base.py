import mox
from flask.ext.testing import TestCase
from resumr import MakeApp

class BaseTest(TestCase, mox.MoxTestBase):

    def create_app(self):
        app = MakeApp()
        app.config['SERVER_NAME'] = 'localhost'
        app.config['SECRET_KEY'] = 'testsecret'
        app.config['TESTING'] = True
        app.config['BYPASS_LOGIN'] = False
        app.testing = True
        return app

    def tearDown(self):
        super( BaseTest, self ).tearDown()
        self.mox.UnsetStubs()
