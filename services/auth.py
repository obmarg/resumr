
from rauth.service import OAuth2Service
from .errors import OAuthException
from .facebook import FacebookService
from .google import GoogleService

__all__ = [ 'SERVICES_AVALIABLE', 'GetAuthService' ]


class BaseOAuth2(object):
    '''
    BaseOAuth2 class that wraps the rauth library and
    handles functionality common to OAuth2Services, that isn't
    dealt with by the rauth library
    '''

    def __init__(
            self, name, config, redirect_uri, scopes,
            serviceClass, **kwargs
            ):
        '''
        Constructor

        Params:
            name                The name of this service
            config              Config object to extract configuration from
            redirect_uri        The uri for the service to redirect to
            scopes              The scopes to request during auth
            serviceClass        The service class to create after auth
            authorize_url       The url for authorizing
            access_token_url    The url for obtaining an access token
                                from an authorization code
        '''
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.serviceClass = serviceClass
        upperName = name.upper()
        oAuthKeyName = upperName + '_OAUTH_KEY'
        oAuthSecretName = upperName + '_OAUTH_SECRET'
        try:
            self.service = OAuth2Service(
                    name=name,
                    authorize_url=kwargs[ 'authorize_url' ],
                    access_token_url=kwargs[ 'access_token_url' ],
                    consumer_key=config[ oAuthKeyName ],
                    consumer_secret=config[ oAuthSecretName ]
                    )
        except KeyError:
            raise Exception(
                    "You must provide {0} and {1} in the config".format(
                        oAuthKeyName, oAuthSecretName
                        ) )

    def GetAuthUrl(self, state=''):
        '''
        Gets the authorize url

        Params:
            state   Optional state variable to use in the url
        '''
        return self.service.get_authorize_url(
                redirect_uri=self.redirect_uri,
                scope=self.scopes,
                state=state
                )

    def ProcessAuthResponse(self, auth_code, **kwargs):
        '''
        Processes an authorization response

        Returns:
            A Service object
        Params:
            auth_code   The auth code supplied by the client
        Raises:
            An OAuthException on error
        '''
        data = {
                'code': auth_code,
                'redirect_uri': self.redirect_uri
                }
        if 'method' in kwargs and kwargs[ 'method' ] == 'GET':
            kwargs[ 'params' ] = data
        else:
            kwargs[ 'data' ] = data
        print "Sending data {0}".format( data )
        rv = self.service.get_access_token( **kwargs )
        if "error" in rv.content:
            raise OAuthException( "OAuth Service returned error - {0}".format(
                rv.content[ 'error' ]
                ) )
        try:
            accessToken = rv.content[ 'access_token' ]
            return self.serviceClass( accessToken )
        except KeyError:
            raise OAuthException( "No access token in response" )


class FacebookAuthService(BaseOAuth2):
    '''
    Facebook auth service

    This is basically the same as the BaseOAuth2 class, but requests it's
    access token using GET instead of POST
    '''

    def ProcessAuthResponse(self, *pargs, **kwargs):
        return super( FacebookAuthService, self ).ProcessAuthResponse(
                method='GET', *pargs, **kwargs
                )

_serviceInfo = {}
_serviceInfo[ 'google' ] = {
        'authClass': BaseOAuth2,
        'serviceClass': GoogleService,
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'access_token_url': 'https://accounts.google.com/o/oauth2/token',
        'scopes': 'https://www.googleapis.com/auth/userinfo#email'
        }
_serviceInfo[ 'facebook' ] = {
        'authClass': FacebookAuthService,
        'serviceClass': FacebookService,
        'authorize_url': 'https://www.facebook.com/dialog/oauth',
        'access_token_url': 'https://graph.facebook.com/oauth/access_token',
        'scopes': 'email'
        }

SERVICES_AVALIABLE = _serviceInfo.keys()
_authServices = {}


def GetAuthService(name, config=None, redirect_url=None):
    '''
    Returns an auth service

    This must be called at least once with all arguments.
    After that, config & redirect_url are optional and will be ignored

    Params:
        name            The name of the service
        config          The configuration to setup the service with
        redirect_url    The url to redirect users to after they've authed
    '''
    global _authServices
    try:
        return _authServices[ name ]
    except KeyError:
        try:
            serviceInfo = _serviceInfo[ name ]
        except KeyError:
            raise Exception( 'No such service: {0}'.format( name ) )
        if config is None or redirect_url is None:
            raise Exception(
                    'GetService needs to be called with all parameters'
                    'at least once for service {0}'.format( name )
                    )
        _authServices[ name ] = serviceInfo[ 'authClass' ](
                name,
                config,
                redirect_url,
                **serviceInfo
                )
        return _authServices[ name ]
