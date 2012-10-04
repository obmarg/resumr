

import mox
import flask.ext.should_dsl
from flask import Flask
from flask.ext.testing import TestCase
from should_dsl import should
from views import SystemTestViews

# Let's keep pyflakes happy
flask.ext.should_dsl
be_200 = None


class TestSystemTestUtils(TestCase, mox.MoxTestBase):

    def create_app(self):
        app = Flask(__name__)
        app.config['SERVER_NAME'] = 'localhost:5000'
        app.config['SECRET_KEY'] = 'testsecret'
        app.config['TESTING'] = True
        app.config['BYPASS_LOGIN'] = False
        app.testing = True
        app.register_blueprint(SystemTestViews, url_prefix='/systemtest')
        return app

    def tearDown(self):
        self.mox.UnsetStubs()

    def it_has_system_test_reset(self):
        self.app.SystemTestReset = self.mox.CreateMockAnything()
        self.app.SystemTestReset()

        self.mox.ReplayAll()
        try:
            self.app.config['SYSTEM_TEST'] = True
            rv = self.client.get('/systemtest/reset')
            self.mox.VerifyAll()
            rv |should| be_200
        finally:
            self.app.config['SYSTEM_TEST'] = False

    def it_has_system_test_logout(self):
        try:
            self.app.config['SYSTEM_TEST'] = True
            self.app.config['BYPASS_LOGIN'] = True
            rv = self.client.get('/systemtest/logout')
            self.assertStatus(rv, 200)
            self.assertEqual(self.app.config['BYPASS_LOGIN'], False)
        finally:
            self.app.config['SYSTEM_TEST'] = False
            self.app.config['BYPASS_LOGIN'] = False
