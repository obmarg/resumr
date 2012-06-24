
import urllib2
import json
from urllib import urlencode
from .errors import OAuthException, ServiceError, UnknownResponse


class FacebookService(object):
    '''
    Class responsible for dealing with facebook API requests
    '''
    GRAPH_URL = 'https://graph.facebook.com'
    ME_URL = GRAPH_URL + '/me'

    def __init__(self, accessToken):
        '''
        Constructor

        Params:
            accessToken   A valid access token for the facebook API
        '''
        if not accessToken:
            raise Exception( "Access token must not be empty" )
        self.accessToken = accessToken

    def _AppendAccessKey(self, url):
        '''
        Utility function that appends an access key to the facebook URL
        '''
        return url + '?' + urlencode({ 'access_token': self.accessToken })

    def GetUserEmail(self):
        '''
        Gets the users email

        Returns:
            The users email from facebook
        Raises:
            URLError        On communication error
            OAuthException  On OAuth error from facebook
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
            if data[ 'error' ][ 'type' ] == 'OAuthException':
                raise OAuthException( data[ 'error' ][ 'message' ] )
            raise ServiceError( data[ 'error' ][ 'message' ] )
        #TODO: It would probably be quite nice to cache the response
        #       in case it's needed for other queries etc.
        #       No need for now though
        try:
            return data[ 'email' ]
        except KeyError:
            raise UnknownResponse(
                    "Unknown response from facebook {0}".format( data )
                    )
