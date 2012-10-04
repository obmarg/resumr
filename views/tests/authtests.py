import flask.ext.should_dsl
from should_dsl import should
from .base import BaseTest

from views import auth
from services.auth import BaseOAuth2, OAuthException
from services.facebook import FacebookService
from flask import session

# Keep pyflakes happy
be_200 = abort_400 = abort_500 = redirect_to = None
flask.ext.should_dsl


class TestLogin(BaseTest):

    def should_display_login_page(self):
        self.mox.StubOutWithMock( auth, 'IsLoggedIn' )
        auth.IsLoggedIn().AndReturn( False )
        self.mox.ReplayAll()
        response = self.client.get( '/login' )
        self.mox.VerifyAll()
        response |should| be_200
        self.assertTemplateUsed( 'login.html' )

    def should_redirect_to_index_if_logged_in(self):
        self.mox.StubOutWithMock( auth, 'IsLoggedIn' )
        auth.IsLoggedIn().AndReturn( True )
        self.mox.ReplayAll()
        self.client.get( '/login' ) |should| redirect_to('/')
        self.mox.VerifyAll()


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
            client.get(
                    '/login/auth/facebook',
                    query_string={ 'code': 'auth_code' }
                    ) |should| redirect_to('/')
            self.assertEqual( 'someone@somewhere', session[ 'email' ] )
        self.mox.VerifyAll()

    def should_handle_user_oauth_error(self):
        self.mox.ReplayAll()
        self.client.get(
                '/login/auth/facebook',
                query_string={ 'error': 'e' }
                ) |should| abort_500
        self.mox.VerifyAll()

    def should_handle_failure_to_get_token(self):
        self.mox.StubOutWithMock( auth, 'GetAuthService' )
        authService = self.mox.CreateMock( BaseOAuth2 )
        self.mox.CreateMock( FacebookService )

        auth.GetAuthService( 'facebook' ).AndReturn( authService )
        authService.ProcessAuthResponse( 'auth_code' ).AndRaise(
                OAuthException
                )

        self.mox.ReplayAll()
        with self.assertRaises( OAuthException ):
            self.client.get(
                    '/login/auth/facebook',
                    query_string={ 'code': 'auth_code' }
                    )
        self.mox.VerifyAll()

    def should_handle_invalid_oauth_redirect(self):
        self.mox.StubOutWithMock( auth, 'GetAuthService' )
        authService = self.mox.CreateMock( BaseOAuth2 )
        self.mox.CreateMock( FacebookService )

        auth.GetAuthService( 'facebook' ).AndReturn( authService )

        self.mox.ReplayAll()
        self.client.get(
                '/login/auth/facebook',
                query_string={ 'something': 'auth_code' }
                ) |should| abort_400
        self.mox.VerifyAll()

