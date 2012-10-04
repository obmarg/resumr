from .base import BaseTest
from views import auth
from views.auth import session, OAuthException
from services.auth import BaseOAuth2
from services.facebook import FacebookService


class TestStylesheetApi(BaseTest):

    def testLogin(self):
        self.mox.StubOutWithMock( auth, 'IsLoggedIn' )
        auth.IsLoggedIn().AndReturn( False )
        self.mox.ReplayAll()
        rv = self.client.get( '/login' )
        self.mox.VerifyAll()
        self.assert200( rv )
        self.assertTemplateUsed( 'login.html' )

    def testLoginAlready(self):
        self.mox.StubOutWithMock( auth, 'IsLoggedIn' )
        auth.IsLoggedIn().AndReturn( True )
        self.mox.ReplayAll()
        rv = self.client.get( '/login' )
        self.mox.VerifyAll()
        self.assertRedirects( rv, '/' )

    def testOAuthCallback(self):
        self.mox.StubOutWithMock( auth, 'GetAuthService' )
        authService = self.mox.CreateMock( BaseOAuth2 )
        service = self.mox.CreateMock( FacebookService )

        auth.GetAuthService( 'facebook' ).AndReturn( authService )
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
        self.mox.StubOutWithMock( auth, 'GetAuthService' )
        authService = self.mox.CreateMock( BaseOAuth2 )
        self.mox.CreateMock( FacebookService )

        auth.GetAuthService( 'facebook' ).AndReturn( authService )
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
        self.mox.StubOutWithMock( auth, 'GetAuthService' )
        authService = self.mox.CreateMock( BaseOAuth2 )
        self.mox.CreateMock( FacebookService )

        auth.GetAuthService( 'facebook' ).AndReturn( authService )

        self.mox.ReplayAll()
        rv = self.client.get(
                '/login/auth/facebook',
                query_string={ 'something': 'auth_code' }
                )
        self.mox.VerifyAll()
        self.assertStatus(rv, 500)

