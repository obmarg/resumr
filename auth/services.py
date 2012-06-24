
from rauth.service import OAuth2Service

__all__ = [ 'SERVICES_AVALIABLE', 'GetService' ]


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
        upperName = name.upper()
        oAuthKeyName = upperName + '_OAUTH_KEY'
        oAuthSecretName = upperName + '_OAUTH_SECRET'
        try:
            super( BaseOAuth2, self ).__init__(
                    name=name,
                    authorize_url=kwargs[ 'authorize_url' ],
                    access_token_url=kwargs[ 'access_token_url' ],
                    consumer_key=config[ oAuthKeyName ],
                    consumer_secret=config[ oAuthSecretName ]
                    )
        except KeyError:
            raise Exception(
                    "You must provide {} and {} in the config".format(
                        oAuthKeyName, oAuthSecretName
                        ) )

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


_serviceInfo = {}
_serviceInfo[ 'google' ] = {
        'serviceClass': BaseOAuth2,
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'access_token_url': 'https://accounts.google.com/o/oauth2/token'
        }
_serviceInfo[ 'facebook' ] = {
        'serviceClass': FacebookService,
        'authorize_url': 'https://www.facebook.com/dialog/oauth',
        'access_token_url': 'https://graph.facebook.com/oauth/access_token'
        }

SERVICES_AVALIABLE = _serviceInfo.keys()
_services = {}


def GetService(name, config=None, redirect_url=None):
    '''
    Returns a service

    This must be called at least once with all arguments.
    After that, config & redirect_url are optional and will be ignored

    Params:
        name            The name of the service
        config          The configuration to setup the service with
        redirect_url    The url to redirect users to after they've authed
    '''
    global _services
    try:
        return _services[ name ]
    except KeyError:
        try:
            serviceInfo = _serviceInfo[ name ]
        except KeyError:
            raise Exception( 'No such service: {}'.format( name ) )
        if config is None or redirect_url is None:
            raise Exception(
                    'GetService needs to be called with all parameters'
                    'at least once for service {}'.format( name )
                    )
        _services[ name ] = serviceInfo[ 'serviceClass' ](
                name,
                config,
                redirect_url,
                **serviceInfo
                )
        return _services[ name ]
