import json
import markdown
from flask import Flask, render_template, abort, request
from db import Document, SectionNotFound

app = Flask(__name__)

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


@app.route('/render')
def Render():
    d = GetDoc()
    sections = [ s for i, s in d.CurrentSections() ]
    sections = [ markdown.markdown( s.CurrentContent() ) for s in sections ]
    return render_template(
            'render.html',
            sections=sections
            )

if __name__ == "__main__":
    app.run(debug=True)
