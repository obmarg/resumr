
from flask import Blueprint, abort, request, redirect, url_for, render_template
from flask import session
from utils.viewutils import IsLoggedIn
from services import GetAuthService, SERVICES_AVALIABLE

app = Blueprint('auth', __name__)


@app.route('/login')
def Login():
    if IsLoggedIn():
        return redirect( url_for( 'index' ) )
    # TODO: Add a state into the auth url stuff
    services = [
            { 'name': s, 'url': GetAuthService( s ).GetAuthUrl() }
            for s in SERVICES_AVALIABLE
            ]
    return render_template('login.html', services=services)


@app.route('/logout')
def Logout():
    if IsLoggedIn():
        del session['regType']
        del session['email']
    return redirect( url_for( 'auth.Login' ) )


@app.route('/login/auth/<serviceName>')
def OAuthCallback(serviceName):
    '''
    OAuth services should redirect the user to this url after auth

    Params:
        serviceName     The name of the service the user is authenticating with
    '''
    if "error" in request.args:
        # TODO: Handle errors properly somehow
        abort( 500 )
    authService = GetAuthService( serviceName )
    remoteService = authService.ProcessAuthResponse(
            request.args[ 'code' ]
            )
    session[ 'regType' ] = serviceName
    session[ 'email' ] = remoteService.GetUserEmail()
    return redirect(url_for( 'index' ))
