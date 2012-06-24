import json
import markdown
from flask import Flask, render_template, abort, request
from db import Document, SectionNotFound
from auth.services import GetService, SERVICES_AVALIABLE, OAuthException


class DefaultConfig(object):
    DEBUG = False
    TESTING = False


class ResumrApp(Flask):
    def __init__(self):
        super( ResumrApp, self ).__init__(__name__)

        self.config.from_object(DefaultConfig)
        self.config.from_envvar('RESUMR_CONFIG', silent=True)
        # Set up the services
        oAuthUrl = '/login/auth/{0}'
        for name in SERVICES_AVALIABLE:
            GetService(
                    name, self.config,
                    oAuthUrl.format( name )
                    )


app = ResumrApp()

docName = 'test'


def GetDoc():
    return Document( docName )


@app.route("/")
def index():
    return render_template('index.html')


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
    return json.dumps( sections )


@app.route('/api/sections/<name>', methods=['GET'])
def GetSection(name):
    ''' Gets the current details of a section '''
    d = GetDoc()
    try:
        s = d.FindSection( name )
    except SectionNotFound:
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
    # TODO: Add some validation of the input (either here or in Document)
    s = d.AddSection( data[ 'newName' ], data[ 'content' ] )
    return json.dumps( {
        'name' : s.name,
        'content' : data[ 'content' ],
        'pos' : s.GetPosition()
        } )


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
        section.SetContent( request.json[ 'content' ] )
        section.SetPosition( request.json[ 'pos' ] )
    except SectionNotFound:
        abort(404)
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
    except SectionNotFound:
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
    except SectionNotFound:
        abort( 404 )
    for i, d in enumerate( s.ContentHistory() ):
        if i == historyId:
            s.SetContent( d )
            return "OK"
    # If we get here, then there's been no history entry found
    abort( 404 )


@app.route('/render')
def Render():
    d = GetDoc()
    sections = [ s for i, s in d.CurrentSections() ]
    sections = [ markdown.markdown( s.CurrentContent() ) for s in sections ]
    return render_template(
            'render.html',
            sections=sections
            )


@app.route('/login')
def Login():
    # TODO: Add a state into the auth url stuff
    services = [
            { 'name': s, 'url': GetService( s ).get_authorize_url() }
            for s in SERVICES_AVALIABLE
            ]
    return render_template('login.html', services=services)


@app.route('/login/auth/<service>')
def OAuthCallback(service):
    '''
    OAuth services should redirect the user to this url after auth

    Params:
        service     The name of the service the user is authenticating with
    '''
    if "error" in request.args:
        # TODO: Handle errors properly somehow
        abort( 500 )
    try:
        return GetService( service ).get_access_token( request.args[ 'code' ] )
    except OAuthException:
        abort( 500 )
    except KeyError:
        abort( 500 )

if __name__ == "__main__":
    app.run()
