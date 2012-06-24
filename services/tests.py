
import unittest
import mox
import auth
from .errors import OAuthException
from collections import namedtuple


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()


class BaseOAuth2Tests(BaseTest):

    def setUp(self):
        super( BaseOAuth2Tests, self ).setUp()
        self.mox.StubOutClassWithMocks( auth, 'OAuth2Service' )

    def createMockService(self):
        # Utility function for tests that need a mock service
        service = auth.OAuth2Service(
                name='serviceName',
                authorize_url='auth_url',
                access_token_url='access_url',
                consumer_key='key',
                consumer_secret='secret'
                )
        return service

    def doConstructor(self):
        # Utility function that runs the OAuth2Service constructor
        # and returns the results
        config = {}
        config[ 'SERVICENAME_OAUTH_KEY' ] = 'key'
        config[ 'SERVICENAME_OAUTH_SECRET' ] = 'secret'
        s = auth.BaseOAuth2(
                'serviceName', config, 'redirect', 'scopes',
                authorize_url='auth_url', access_token_url='access_url'
                )
        return s

    def testConstructor(self):
        self.createMockService()
        self.mox.ReplayAll()
        s = self.doConstructor()
        self.assertIsNot( s, None )
        self.mox.VerifyAll()

    def testConstructorMissingKey(self):
        self.mox.ReplayAll()
        config = {}
        config[ 'OTHERSERVICE_OAUTH_KEY' ] = 'key'
        config[ 'SERVICENAME_OAUTH_SECRET' ] = 'secret'
        with self.assertRaises( Exception ):
            auth.BaseOAuth2(
                    'serviceName', config, 'redirect', 'scopes',
                    authorize_url='auth_url', access_token_url='access_url'
                    )
        self.mox.VerifyAll()

    def testConstructorMissingSecret(self):
        self.mox.ReplayAll()
        config = {}
        config[ 'SERVICENAME_OAUTH_KEY' ] = 'key'
        config[ 'OTHERSERVICE_OAUTH_SECRET' ] = 'secret'
        with self.assertRaises( Exception ):
            auth.BaseOAuth2(
                    'serviceName', config, 'redirect', 'scopes',
                    authorize_url='auth_url', access_token_url='access_url'
                    )
        self.mox.VerifyAll()

    def testGetUrl(self):
        s = self.createMockService()
        s.get_authorize_url(
                redirect_uri='redirect',
                scope='scopes',
                state='state'
                ).AndReturn( 'an_auth_url' )
        self.mox.ReplayAll()
        s = self.doConstructor()
        authUrl = s.GetAuthUrl('state')
        self.mox.VerifyAll()
        self.assertEqual( 'an_auth_url', authUrl )

    def testProcessResponse(self):
        s = self.createMockService()
        ResponseType = namedtuple( 'ResponseType', [ 'content' ] )
        response = ResponseType( content={ 'access_token': 'access' } )
        s.get_access_token(data={
            'code': 'auth_code', 'redirect_uri': 'redirect'
            }).AndReturn( response )
        self.mox.ReplayAll()

        s = self.doConstructor()
        s.ProcessAuthResponse( 'auth_code' )
        self.mox.VerifyAll()
        self.assertEqual( 'access', s.accessToken )

    def testProcessResponseError(self):
        s = self.createMockService()
        ResponseType = namedtuple( 'ResponseType', [ 'content' ] )
        response = ResponseType( content={ 'error': 'error text' } )
        s.get_access_token(data={
            'code': 'auth_code', 'redirect_uri': 'redirect'
            }).AndReturn( response )
        self.mox.ReplayAll()

        s = self.doConstructor()

        with self.assertRaises( OAuthException ):
            s.ProcessAuthResponse( 'auth_code' )

        self.mox.VerifyAll()

    def testProcessResponseMissingToken(self):
        s = self.createMockService()
        ResponseType = namedtuple( 'ResponseType', [ 'content' ] )
        response = ResponseType( content={} )
        s.get_access_token(data={
            'code': 'auth_code', 'redirect_uri': 'redirect'
            }).AndReturn( response )
        self.mox.ReplayAll()

        s = self.doConstructor()

        with self.assertRaises( OAuthException ):
            s.ProcessAuthResponse( 'auth_code' )

        self.mox.VerifyAll()


class FacebookAuthTests(BaseTest):

    def testProcessAuthResponse(self):
        self.mox.StubOutClassWithMocks( auth, 'OAuth2Service' )

        s = auth.OAuth2Service(
                name='serviceName',
                authorize_url='auth_url',
                access_token_url='access_url',
                consumer_key='key',
                consumer_secret='secret'
                )
        ResponseType = namedtuple( 'ResponseType', [ 'content' ] )
        response = ResponseType( content={ 'access_token': 'access' } )
        s.get_access_token(method='GET', data={
            'code': 'auth_code', 'redirect_uri': 'redirect'
            }).AndReturn( response )
        self.mox.ReplayAll()

        config = {}
        config[ 'SERVICENAME_OAUTH_KEY' ] = 'key'
        config[ 'SERVICENAME_OAUTH_SECRET' ] = 'secret'
        s = auth.FacebookAuthService(
                'serviceName', config, 'redirect', 'scopes',
                authorize_url='auth_url', access_token_url='access_url'
                )

        s.ProcessAuthResponse( 'auth_code' )
        self.mox.VerifyAll()
        self.assertEqual( 'access', s.accessToken )


# TODO: Write GetAuthService tests
