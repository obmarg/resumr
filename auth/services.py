
from rauth.service import OAuth2Service


class BaseOAuth2(OAuth2Service):
    '''
    BaseOAuth2 class that handles functionality common to
    OAuth2Services, that isn't covered by the rauth library
    '''

    def __init__(self, name, config, redirect_uri, **kwargs):
        '''
        Constructor

        Params:
            name                The name of this service
            config              Config object to extract configuration from
            redirect_uri        The uri for the service to redirect to
            authorize_url       The url for authorizing
            access_token_url    The url for obtaining an access token
                                from an authorization code
        '''
        self.redirect_uri = redirect_uri
        upperName = config.upper()
        super( BaseOAuth2, self ).__init__(
                name=name,
                authorize_url='',
                access_token_url='',
                consumer_key=config[ upperName + '_OAUTH_KEY' ],
                consumer_secret=config[ upperName + '_OAUTH_SECRET' ]
                )

    def get_authorize_url(self, state=''):
        '''
        Gets the authorize url

        Params:
            state   Optional state variable to use in the url
        '''
        return super( BaseOAuth2, self ).get_authorize_url(
                redirect_uri=self.redirect_uri,
                scope='',
                state=state
                )

    def get_access_token(self, auth_code):
        '''
        Gets the access token from the authorization code

        Params:
            auth_code   The auth code supplied by the client
        '''
        data = {
                'code': auth_code,
                'redirect_uri': self.redirect_uri
                }
        return super( BaseOAuth2, self ).get_access_token( data=data )


class FacebookService(BaseOAuth2):
    '''
    Facebook auth service

    This is basically the same as the BaseOAuth2 class, but requests it's
    access token using GET instead of POST
    '''

    def get_access_token(self, **kwargs):
        return super( FacebookService, self ).get_access_token(
                method='GET', **kwargs
                )

_googleService = None
_facebookService = None


def GetGoogleService(config, redirect_url):
    global _googleService
    if _googleService is None:
        _googleService = BaseOAuth2(
                'google',
                config,
                redirect_url,
                authorize_url='https://accounts.google.com/o/oauth2/auth',
                access_token_url='https://accounts.google.com/o/oauth2/token'
                )
    return _googleService


def GetFacebookService(config, redirect_url):
    global _facebookService
    if _facebookService is None:
        _facebookService = FacebookService(
                'facebook',
                config,
                redirect_url,
                authorize_url='https://www.facebook.com/dialog/oauth',
                access_token_url='https://graph.facebook.com/oauth/access_token'
                )
    return _facebookService

