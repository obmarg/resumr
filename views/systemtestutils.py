
from flask import Blueprint, current_app, abort

app = Blueprint('systemtest', __name__)


@app.route( '/reset' )
def SystemTestReset():
    '''
    Called by system tests to reset all data
    '''
    if not current_app.config[ 'SYSTEM_TEST' ]:
        abort( 403 )
    current_app.SystemTestReset()
    return "OK"


@app.route( '/logout' )
def SystemTestLogout():
    '''
    Called by system tests to logout
    '''
    if not current_app.config[ 'SYSTEM_TEST' ]:
        abort( 403 )
    current_app.config[ 'BYPASS_LOGIN' ] = False
    return "OK"

