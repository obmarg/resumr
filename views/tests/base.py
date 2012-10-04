import mox
from flask.ext.testing import TestCase
from resumr import MakeApp


class BaseTest(TestCase, mox.MoxTestBase):
    RemoveFlaskTestingContext = True

    def create_app(self):
        app = MakeApp()
        app.config['SERVER_NAME'] = 'localhost'
        app.config['SECRET_KEY'] = 'testsecret'
        app.config['TESTING'] = True
        app.config['BYPASS_LOGIN'] = False
        app.testing = True
        return app

    def setUp(self):
        super(BaseTest, self,).setUp()
        if self.RemoveFlaskTestingContext and self._ctx:
            # Pop the request context created by flask-testing.
            # It messes with exception throw->catch stuff
            self._ctx.pop()
            self._ctx = None

    def tearDown(self):
        super(BaseTest, self).tearDown()
        self.mox.UnsetStubs()
