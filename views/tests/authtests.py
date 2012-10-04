from .base import BaseTest
from views import auth
from views.auth import session, OAuthException
from services.auth import BaseOAuth2
from services.facebook import FacebookService


class TestLogin(BaseTest):

    def should_display_login_page(self):
        self.mox.StubOutWithMock( auth, 'IsLoggedIn' )
        auth.IsLoggedIn().AndReturn( False )
        self.mox.ReplayAll()
        rv = self.client.get( '/login' )
        self.mox.VerifyAll()
        self.assert200( rv )
        self.assertTemplateUsed( 'login.html' )

    def should_redirect_to_index_if_logged_in(self):
        self.mox.StubOutWithMock( auth, 'IsLoggedIn' )
        auth.IsLoggedIn().AndReturn( True )
        self.mox.ReplayAll()
        rv = self.client.get( '/login' )
        self.mox.VerifyAll()
        self.assertRedirects( rv, '/' )


class TestOAuthCallback(BaseTest):

    def should_handle_success(self):
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

    def should_handle_user_oauth_error(self):
        self.mox.ReplayAll()
        rv = self.client.get(
                '/login/auth/facebook',
                query_string={ 'error': 'e' }
                )
        self.mox.VerifyAll()
        self.assertStatus(rv, 500)

    def should_handle_failure_to_get_token(self):
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

    def should_handle_invalid_oauth_redirect(self):
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

