import json
import markdown
import shutil
import sys
import re
from flask import Flask, render_template, abort, request, session
from flask import redirect, url_for
from db import Document, ContentNotFound, RepoNotFound
from services import GetAuthService, SERVICES_AVALIABLE, OAuthException
from utils.markdownutils import ValidateMarkdown, MarkdownValidationError
from utils.markdownutils import CleanMarkdownOutput

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

SECTION_NAME_REGEXP = re.compile(r'^\w+$')


def IsLoggedIn():
    '''
    Function that checks if we're logged in

    Returns:
        True if we are, False otherwise
    '''
    if app.config[ 'BYPASS_LOGIN' ]:
        return True
    if session.new or 'email' not in session:
        return False
    return True


def GetDoc():
    if not IsLoggedIn():
        abort( 401 )
    if app.config[ 'BYPASS_LOGIN' ]:
        docName = app.config[ 'BYPASS_REPO_NAME' ]
    else:
        try:
            docName = '{0} - {1}'.format(
                    session[ 'regType' ], session[ 'email' ]
                    )
        except KeyError:
            # Seems like we're not logged in after all :(
            abort( 401 )
    try:
        return Document( docName, rootPath=app.config[ 'DATA_PATH' ] )
    except RepoNotFound:
        return Document(
                docName, create=True, rootPath=app.config[ 'DATA_PATH' ]
                )


@app.route("/")
def index():
    if IsLoggedIn():
        return render_template('index.html')
    return redirect( url_for( 'Login' ) )


##############
#
# Sections API
#
##############


@app.route('/api/sections', methods=['GET'])
def ListSections():
    ''' Lists the current sections including order '''
    d = GetDoc()
    sections = [ {
                'name' : s.name,
                'pos' : i,
                'content' : s.CurrentContent()
                } for i, s in d.CurrentSections() ]
    # TODO: Maybe make this return an object
    #       Seem to remember some security warning for
    #       returning lists
    #       Probably want to use jsonify (?) as well
    return json.dumps( sections )


@app.route('/api/sections/<name>', methods=['GET'])
def GetSection(name):
    ''' Gets the current details of a section '''
    d = GetDoc()
    try:
        s = d.FindSection( name )
    except ContentNotFound:
        abort( 404 )
    return json.dumps({
        'name': s.name,
        'pos': s.GetPosition(),
        'content': s.CurrentContent()
        })


@app.route('/api/sections', methods=['POST'])
def AddSection():
    '''
    Adds a section.
    '''
    d = GetDoc()
    data = request.json
    try:
        try:
            name = data[ 'newName' ]
        except KeyError:
            # We check data['name'] for the sake of component tests.
            # The javascript clientside should send via newName,
            # as otherwise it mistakes the new section for an existing
            # one, and attempts to PUT
                name = data[ 'name' ]
        if not SECTION_NAME_REGEXP.match(name):
            abort(500)
        content = data['content']
        ValidateMarkdown(content)
        s = d.AddSection(name, content)
        return json.dumps({
            'name': s.name,
            'content': content,
            'pos': s.GetPosition()
            })
    except KeyError:
        abort(500)
    except MarkdownValidationError:
        abort(500)


@app.route('/api/sections/<name>', methods=['PUT'])
def UpdateSection(name):
    '''
    Updates a sections contents

    Args:
        name    The name of the section to update
    '''
    d = GetDoc()
    try:
        section = d.FindSection( name )
        content = request.json[ 'content' ]
        if section.CurrentContent() != content:
            ValidateMarkdown(content)
            section.SetContent(content)
        if section.GetPosition() != request.json[ 'pos' ]:
            section.SetPosition( request.json[ 'pos' ] )
    except ContentNotFound:
        abort(404)
    except MarkdownValidationError:
        abort(500)
    return "OK"


@app.route('/api/sections/<name>', methods=['DELETE'])
def RemoveSection(name):
    '''
    Removes a section

    Args:
        name    The name of the section to remove
    '''
    d = GetDoc()
    d.RemoveSection( name )
    return "OK"


@app.route('/api/sections/<name>/history', methods=['GET'])
def SectionHistory(name):
    '''
    Gets the history for a section

    Args:
        name    The name of the section

    Notes:
        Currently this just returns the entire history,
        but it might be more efficient to just return a few at a time,
        and include a "next" link.  That way we can do some lazy loading,
        which should save downloading potentially hundreds of entries when
        we just need a few
    '''
    d = GetDoc()
    try:
        s = d.FindSection( name )
    except ContentNotFound:
        abort( 404 )
    data = []
    for i, d in enumerate( s.ContentHistory() ):
        # This isn't ideal, since the id's will change after another revision
        # is added, but it should do for an initial version
        data.append( { 'id' : i, 'content' : d } )
    return json.dumps( data )


@app.route(
    '/api/sections/<name>/history/select/<int:historyId>',
    methods=['POST']
    )
def SelectSectionHistory( name, historyId ):
    '''
    Updates a section to make a certain history entry it's head

    Args:
        name        The name of the section
        historyId   The id of the history entry to use
    '''
    d = GetDoc()
    try:
        s = d.FindSection( name )
    except ContentNotFound:
        abort( 404 )
    for i, d in enumerate( s.ContentHistory() ):
        if i == historyId:
            s.SetContent( d )
            return "OK"
    # If we get here, then there's been no history entry found
    abort( 404 )


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
