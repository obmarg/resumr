from resumr import MakeApp
import mox
from flask import session
from flask.ext.testing import TestCase
from utils import viewutils
from utils.viewutils import IsLoggedIn, GetDoc
from db import RepoNotFound


class TestIsLoggedIn(TestCase, mox.MoxTestBase):

    def create_app(self):
        app = MakeApp()
        app.config['SERVER_NAME'] = 'localhost:5000'
        app.config['SECRET_KEY'] = 'testsecret'
        app.config['TESTING'] = True
        app.config['BYPASS_LOGIN'] = False
        app.testing = True
        return app

    def tearDown(self):
        self.mox.UnsetStubs()

    def must_return_false_on_new_session(self):
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            assert not IsLoggedIn()

    def must_return_true_on_bypass_login(self):
        self.app.config['BYPASS_LOGIN'] = True
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            assert IsLoggedIn()

    def must_return_true_if_logged_in(self):
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            session.new = False
            session[ 'email' ] = 'something'
            assert viewutils.IsLoggedIn()


class TestGetDoc(TestCase, mox.MoxTestBase):

    def create_app(self):
        app = MakeApp()
        app.config['SERVER_NAME'] = 'localhost:5000'
        app.config['SECRET_KEY'] = 'testsecret'
        app.config['TESTING'] = True
        app.config['BYPASS_LOGIN'] = False
        app.testing = True
        return app

    def tearDown(self):
        self.mox.UnsetStubs()

    def should_return_document_when_logged_in(self):
        self.mox.StubOutClassWithMocks(viewutils, 'Document')
        d = viewutils.Document( 'facebook - something', rootPath=None )

        self.mox.ReplayAll()
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            session.new = False
            session[ 'email' ] = 'something'
            session[ 'regType' ] = 'facebook'
            self.assertIs( GetDoc(), d )
        self.mox.VerifyAll()

    def should_use_data_path_config(self):
        self.mox.StubOutClassWithMocks(viewutils, 'Document')
        d = viewutils.Document( 'facebook - something', rootPath='somewhere' )

        self.mox.ReplayAll()
        try:
            self.app.config[ 'DATA_PATH' ] = 'somewhere'
            with self.app.test_request_context('/'):
                self.app.preprocess_request()
                session.new = False
                session[ 'email' ] = 'something'
                session[ 'regType' ] = 'facebook'
                self.assertIs( GetDoc(), d )
            self.mox.VerifyAll()
        finally:
            self.app.config[ 'DATA_PATH' ] = None

    def should_abort_if_not_logged_in(self):
        self.mox.StubOutWithMock(viewutils, 'IsLoggedIn')
        self.mox.StubOutWithMock(viewutils, 'abort')
        viewutils.IsLoggedIn().AndReturn( False )
        viewutils.abort( 401 ).AndRaise( Exception )

        self.mox.ReplayAll()
        with self.assertRaises( Exception ):
            GetDoc()
        self.mox.VerifyAll()

    def should_except_on_missing_keys(self):
        self.mox.StubOutWithMock(viewutils, 'IsLoggedIn')
        self.mox.StubOutWithMock(viewutils, 'abort')
        viewutils.IsLoggedIn().AndReturn( True )
        viewutils.abort( 401 ).AndRaise( Exception )

        self.mox.ReplayAll()
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            with self.assertRaises( Exception ):
                GetDoc()
        self.mox.VerifyAll()

    def should_create_document_if_needed(self):
        self.mox.StubOutWithMock(viewutils, 'Document' )
        viewutils.Document(
                'facebook - something', rootPath=None
                ).AndRaise( RepoNotFound )
        viewutils.Document(
                'facebook - something', create=True, rootPath=None
                ).AndReturn( 'document')

        self.mox.ReplayAll()
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            session.new = False
            session[ 'email' ] = 'something'
            session[ 'regType' ] = 'facebook'
            self.assertEqual( GetDoc(), 'document' )
        self.mox.VerifyAll()
