
import urllib2
import json
from urllib import urlencode
from .errors import OAuthException, ServiceError, UnknownResponse


class GoogleService(object):
    '''
    Class responsible for dealing with Google API requests
    '''
    ME_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'

    def __init__(self, accessToken):
        '''
        Constructor

        Params:
            accessToken   A valid access token for the google API
        '''
        if not accessToken:
            raise Exception( "Access token must not be empty" )
        self.accessToken = accessToken

    def _AppendAccessKey(self, url):
        '''
        Utility function that appends an access key to the google URL
        '''
        return url + '?' + urlencode({ 'access_token': self.accessToken })

    def GetUserEmail(self):
        '''
        Gets the users ID

        Returns:
            The users email from google
        Raises:
            URLError        On communication error
            OAuthException  On OAuth error from google
            ServiceError    On unknown remote error
            UnknownResponse On unknown server response
        '''
        remoteResource = urllib2.urlopen(
                self._AppendAccessKey( self.ME_URL )
                )
        data = remoteResource.read()
        remoteResource.close()
        data = json.loads( data )
        if 'error' in data:
            for err in data[ 'error' ][ 'errors' ]:
                if err[ 'domain' ] == 'com.google.auth':
                    raise OAuthException( err[ 'message' ] )
            raise ServiceError( data[ 'error' ][ 'message' ] )
        #TODO: It would probably be quite nice to cache the response
        #       in case it's needed for other queries etc.
        #       No need for now though
        try:
            return data[ 'email' ]
        except KeyError:
            raise UnknownResponse(
                    "Unknown response from google {0}".format( data )
                    )
