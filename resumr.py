import json
from flask import Flask, render_template
from db import Document

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
                'content' : s.CurrentContent() 
                } for s d.Sections() ]
    # TODO: Maybe make this return an object
    #       Seem to remember some security warning for
    #       returning lists
    return json.dumps( sections )

if __name__ == "__main__":
    app.run()
