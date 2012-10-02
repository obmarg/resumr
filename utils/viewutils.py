
from flask import abort, session, current_app
from db import Document, RepoNotFound


def IsLoggedIn():
    '''
    Function that checks if we're logged in

    Returns:
        True if we are, False otherwise
    '''
    if current_app.config[ 'BYPASS_LOGIN' ]:
        return True
    if session.new or 'email' not in session:
        return False
    return True


def GetDoc():
    if not IsLoggedIn():
        abort( 401 )
    if current_app.config[ 'BYPASS_LOGIN' ]:
        docName = current_app.config[ 'BYPASS_REPO_NAME' ]
    else:
        try:
            docName = '{0} - {1}'.format(
                    session[ 'regType' ], session[ 'email' ]
                    )
        except KeyError:
            # Seems like we're not logged in after all :(
            abort( 401 )
    try:
        return Document(docName, rootPath=current_app.config['DATA_PATH'])
    except RepoNotFound:
        return Document(
                docName, create=True, rootPath=current_app.config['DATA_PATH']
                )
