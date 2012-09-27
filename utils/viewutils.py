
from flask import abort, session
from db import Document, RepoNotFound

_config = None


def SetConfig(config):
    '''
    Sets the config variable for use by the functions in
    this file
    '''
    global _config
    _config = config


def IsLoggedIn():
    '''
    Function that checks if we're logged in

    Returns:
        True if we are, False otherwise
    '''
    if _config[ 'BYPASS_LOGIN' ]:
        return True
    if session.new or 'email' not in session:
        return False
    return True


def GetDoc():
    if not IsLoggedIn():
        abort( 401 )
    if _config[ 'BYPASS_LOGIN' ]:
        docName = _config[ 'BYPASS_REPO_NAME' ]
    else:
        try:
            docName = '{0} - {1}'.format(
                    session[ 'regType' ], session[ 'email' ]
                    )
        except KeyError:
            # Seems like we're not logged in after all :(
            abort( 401 )
    try:
        return Document( docName, rootPath=_config[ 'DATA_PATH' ])
    except RepoNotFound:
        return Document(
                docName, create=True, rootPath=_config[ 'DATA_PATH' ]
                )
