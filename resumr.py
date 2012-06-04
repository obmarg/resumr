import json
from flask import Flask, render_template, abort, request
from db import Document, SectionNotFound

app = Flask(__name__)

docName = 'test'


def GetDoc():
    return Document( docName )


@app.route("/")
def hello():
    return render_template('index.html')


@app.route('/api/sections')
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


if __name__ == "__main__":
    app.run()
