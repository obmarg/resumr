
import unittest
import mox
import auth
import facebook
import google
from collections import namedtuple
from urllib2 import URLError
from .errors import OAuthException, ServiceError, UnknownResponse


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()


class BaseOAuth2Tests(BaseTest):

    def setUp(self):
        super( BaseOAuth2Tests, self ).setUp()
        self.mox.StubOutClassWithMocks( auth, 'OAuth2Service' )
        self.mox.StubOutClassWithMocks( auth, 'GoogleService' )

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
                serviceClass=auth.GoogleService,
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
                    serviceClass=auth.GoogleService,
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
                    serviceClass=auth.GoogleService,
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
        gService = auth.GoogleService( 'access' )
        self.mox.ReplayAll()

        s = self.doConstructor()
        service = s.ProcessAuthResponse( 'auth_code' )
        self.mox.VerifyAll()
        self.assertIs( gService, service )

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
        self.mox.StubOutClassWithMocks( auth, 'FacebookService' )

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
        fbService = auth.FacebookService( 'access' )
        self.mox.ReplayAll()

        config = {}
        config[ 'SERVICENAME_OAUTH_KEY' ] = 'key'
        config[ 'SERVICENAME_OAUTH_SECRET' ] = 'secret'
        s = auth.FacebookAuthService(
                'serviceName', config, 'redirect', 'scopes',
                serviceClass=auth.FacebookService,
                authorize_url='auth_url', access_token_url='access_url'
                )

        service = s.ProcessAuthResponse( 'auth_code' )
        self.mox.VerifyAll()
        self.assertIs( fbService, service )


# TODO: Write GetAuthService tests


class FacebookServiceTests(BaseTest):

    def setUp(self):
        super( FacebookServiceTests, self ).setUp()
        self.mox.StubOutWithMock( facebook.urllib2, 'urlopen' )
        self.mox.StubOutWithMock( facebook.json, 'loads' )

    def setupFetchMocks(self, data):
        # Utility function that sets up mocks for most of the fetch process
        # data param specifies what data should be returned from json
        remoteResource = self.mox.CreateMockAnything()
        facebook.urllib2.urlopen(
                'https://graph.facebook.com/me?access_token=abc'
                ).AndReturn( remoteResource )
        remoteResource.read().AndReturn( 'somejson' )
        remoteResource.close()

        facebook.json.loads( 'somejson' ).AndReturn( data )

    def testConstructEmptyAccessToken(self):
        with self.assertRaises( Exception ):
            facebook.FacebookService( '' )

    def testGetUserEmail(self):
        data = { 'email': 'someone@somewhere.net' }
        self.setupFetchMocks( data )

        self.mox.ReplayAll()
        fb = facebook.FacebookService( 'abc' )
        email = fb.GetUserEmail()
        self.mox.VerifyAll()
        self.assertEqual( 'someone@somewhere.net', email )

    def testGetUserEmailNetworkProblem(self):
        def RaiseUrlError(x):
            raise URLError( 'blah' )

        facebook.urllib2.urlopen(
                'https://graph.facebook.com/me?access_token=abc'
                ).WithSideEffects( RaiseUrlError )

        self.mox.ReplayAll()
        fb = facebook.FacebookService( 'abc' )
        with self.assertRaises( URLError ):
            fb.GetUserEmail()
        self.mox.VerifyAll()

    def testGetUserEmailOAuthException(self):
        data = { 'error': {
            'type': 'OAuthException',
            'message': 'test exception'
            }}
        self.setupFetchMocks( data )

        self.mox.ReplayAll()
        fb = facebook.FacebookService( 'abc' )
        with self.assertRaises( OAuthException ):
            fb.GetUserEmail()
        self.mox.VerifyAll()

    def testGetUserEmailServiceError(self):
        data = { 'error': {
            'type': 'unknown',
            'message': 'test exception'
            }}
        self.setupFetchMocks( data )

        self.mox.ReplayAll()
        fb = facebook.FacebookService( 'abc' )
        with self.assertRaises( ServiceError ):
            fb.GetUserEmail()
        self.mox.VerifyAll()

    def testGetUserEmailUnknownResponse(self):
        data = { 'something': 'someone' }
        self.setupFetchMocks( data )

        self.mox.ReplayAll()
        fb = facebook.FacebookService( 'abc' )
        with self.assertRaises( UnknownResponse ):
            fb.GetUserEmail()
        self.mox.VerifyAll()


class GoogleServiceTests(BaseTest):

    def setUp(self):
        super( GoogleServiceTests, self ).setUp()
        self.mox.StubOutWithMock( google.urllib2, 'urlopen' )
        self.mox.StubOutWithMock( google.json, 'loads' )

    def setupFetchMocks(self, data):
        # Utility function that sets up mocks for most of the fetch process
        # data param specifies what data should be returned from json
        remoteResource = self.mox.CreateMockAnything()
        google.urllib2.urlopen(
                'https://www.googleapis.com/oauth2/v1/userinfo'
                '?access_token=abc'
                ).AndReturn( remoteResource )
        remoteResource.read().AndReturn( 'somejson' )
        remoteResource.close()

        google.json.loads( 'somejson' ).AndReturn( data )

    def testConstructEmptyAccessToken(self):
        with self.assertRaises( Exception ):
            google.GoogleService( '' )

    def testGetUserEmail(self):
        data = { 'email': 'someone@somewhere.net' }
        self.setupFetchMocks( data )

        self.mox.ReplayAll()
        g = google.GoogleService( 'abc' )
        email = g.GetUserEmail()
        self.mox.VerifyAll()
        self.assertEqual( 'someone@somewhere.net', email )

    def testGetUserEmailNetworkProblem(self):
        def RaiseUrlError(x):
            raise URLError( 'blah' )

        google.urllib2.urlopen(
                'https://www.googleapis.com/oauth2/v1/userinfo'
                '?access_token=abc'
                ).WithSideEffects( RaiseUrlError )

        self.mox.ReplayAll()
        g = google.GoogleService( 'abc' )
        with self.assertRaises( URLError ):
            g.GetUserEmail()
        self.mox.VerifyAll()

    def testGetUserEmailOAuthException(self):
        data = { 'error': {
            'errors': [{ 'domain': 'com.google.auth', 'message': 'msg' }],
            'message': 'test exception'
            }}
        self.setupFetchMocks( data )

        self.mox.ReplayAll()
        g = google.GoogleService( 'abc' )
        with self.assertRaises( OAuthException ):
            g.GetUserEmail()
        self.mox.VerifyAll()

    def testGetUserEmailServiceError(self):
        data = { 'error': {
            'errors': [{ 'domain': 'com.google.other', 'message': 'msg' }],
            'message': 'test exception'
            }}
        self.setupFetchMocks( data )

        self.mox.ReplayAll()
        g = google.GoogleService( 'abc' )
        with self.assertRaises( ServiceError ):
            g.GetUserEmail()
        self.mox.VerifyAll()

    def testGetUserEmailUnknownResponse(self):
        data = { 'something': 'someone' }
        self.setupFetchMocks( data )

        self.mox.ReplayAll()
        g = google.GoogleService( 'abc' )
        with self.assertRaises( UnknownResponse ):
            g.GetUserEmail()
        self.mox.VerifyAll()
