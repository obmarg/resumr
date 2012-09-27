import json
import markdown
import shutil
import sys
from flask import Flask, render_template, abort, request, session
from flask import redirect, url_for
from services import GetAuthService, SERVICES_AVALIABLE, OAuthException
from utils.markdownutils import CleanMarkdownOutput
import utils.viewutils
from utils.viewutils import IsLoggedIn, GetDoc
from views.api import SectionApi

SYSTEMTEST_PORT = 43001


class DefaultConfig(object):
    SERVER_NAME = ''
    SECRET_KEY = ''
    DEBUG = False
    TESTING = False
    FACEBOOK_OAUTH_KEY = ''
    FACEBOOK_OAUTH_SECRET = ''
    GOOGLE_OAUTH_KEY = ''
    GOOGLE_OAUTH_SECRET = ''
    BYPASS_LOGIN = False
    BYPASS_REPO_NAME = 'test'
    DATA_PATH = None
    SYSTEM_TEST = False
    MAX_STYLESHEET_SIZE = 1024 * 512


class ResumrApp(Flask):
    def __init__(self):
        super( ResumrApp, self ).__init__(__name__)

        self.config.from_object(DefaultConfig)
        self.config.from_envvar('RESUMR_CONFIG', silent=True)
        utils.viewutils.SetConfig(self.config)

        # Set up the services
        oAuthUrl = 'http://' + self.config[ 'SERVER_NAME' ] + '/login/auth/{0}'
        for name in SERVICES_AVALIABLE:
            GetAuthService(
                    name, self.config,
                    oAuthUrl.format( name )
                    )

    def SystemTestMode(self):
        # Called to activate system test mode for use w/ cucumber
        self.config[ 'SERVER_NAME' ] = '127.0.0.1:{0}'.format(
                SYSTEMTEST_PORT
                )
        self.config[ 'DEBUG' ] = True
        self.config[ 'SYSTEM_TEST' ] = True
        self.config[ 'DATA_PATH' ] = 'systemtestdata'
        self.SystemTestReset()

    def SystemTestReset(self):
        shutil.rmtree( app.config[ 'DATA_PATH' ], ignore_errors=True )
        self.config[ 'BYPASS_LOGIN' ] = True


app = ResumrApp()
app.register_blueprint(SectionApi, url_prefix='/api/sections')


@app.route("/")
def index():
    if IsLoggedIn():
        return render_template('index.html')
    return redirect( url_for( 'Login' ) )

#############
#
# Stylesheet API
#
#############


@app.route( '/api/stylesheet', methods=['GET'] )
def GetStylesheet():
    '''
    Gets the current stylesheet contents
    '''
    d = GetDoc()
    stylesheet = d.GetStylesheet()
    return json.dumps({'content': stylesheet.CurrentContent()})


@app.route('/api/stylesheet/history', methods=['GET'])
def GetStylesheetHistory():
    '''
    Gets the history of the stylesheet
    '''
    d = GetDoc()
    stylesheet = d.GetStylesheet()
    data = [{'content': c} for c in stylesheet.ContentHistory()]
    return json.dumps(data)


@app.route('/api/stylesheet', methods=['PUT'])
def SetStylesheetContent():
    '''
    Sets the current content of the stylesheet
    '''
    d = GetDoc()
    stylesheet = d.GetStylesheet()
    try:
        content = request.json['content']
        if len(content) > app.config['MAX_STYLESHEET_SIZE']:
            abort( 500 )
        # TODO: need to validate the content is actually css/less
    except KeyError:
        abort( 500 )
    if stylesheet.CurrentContent() != content:
        stylesheet.SetContent( content )
    return "OK"

#############
#
# Misc routes
#
#############


@app.route('/render')
def Render():
    if not IsLoggedIn():
        return redirect( url_for( 'Login' ) )
    d = GetDoc()
    Convert = lambda x: CleanMarkdownOutput(markdown.markdown(x))
    sections = [(s.name, s.CurrentContent()) for i, s in d.CurrentSections()]
    output = [
            dict(name=name, content=Convert(content))
            for name, content in sections
            ]

    return render_template(
            'render.html',
            sections=output,
            stylesheet=d.GetStylesheet().CurrentContent()
            )


##########
#
# Authentication Routes
#
##########


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
    return redirect( url_for( 'Login' ) )


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
    try:
        authService = GetAuthService( serviceName )
        remoteService = authService.ProcessAuthResponse(
                request.args[ 'code' ]
                )
        session[ 'regType' ] = serviceName
        session[ 'email' ] = remoteService.GetUserEmail()
        return redirect(url_for( 'index' ))
    except OAuthException:
        abort( 500 )
    except KeyError:
        abort( 500 )
    # TODO: Handle the various other error types here


#############
#
# System Test Utils
#
#############


@app.route( '/systemtest/reset' )
def SystemTestReset():
    '''
    Called by system tests to reset all data
    '''
    if not app.config[ 'SYSTEM_TEST' ]:
        abort( 403 )
    app.SystemTestReset()
    return "OK"


@app.route( '/systemtest/logout' )
def SystemTestLogout():
    '''
    Called by system tests to logout
    '''
    if not app.config[ 'SYSTEM_TEST' ]:
        abort( 403 )
    app.config[ 'BYPASS_LOGIN' ] = False
    return "OK"

if __name__ == "__main__":
    args = {}
    if len( sys.argv ) > 1:
        if sys.argv[1] == 'systemtest':
            print "Running in system test mode"
            args['port'] = SYSTEMTEST_PORT
            app.SystemTestMode()
    app.run(**args)
