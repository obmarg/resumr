
import json
from flask import Blueprint, abort, request, current_app
from utils.viewutils import GetDoc

app = Blueprint('stylesheet_api', __name__)


@app.route( '', methods=['GET'] )
def GetStylesheet():
    '''
    Gets the current stylesheet contents
    '''
    d = GetDoc()
    stylesheet = d.GetStylesheet()
    return json.dumps({'content': stylesheet.CurrentContent()})


@app.route('/history', methods=['GET'])
def GetStylesheetHistory():
    '''
    Gets the history of the stylesheet
    '''
    d = GetDoc()
    stylesheet = d.GetStylesheet()
    data = [{'content': c} for c in stylesheet.ContentHistory()]
    return json.dumps(data)


@app.route('', methods=['PUT'])
def SetStylesheetContent():
    '''
    Sets the current content of the stylesheet
    '''
    d = GetDoc()
    stylesheet = d.GetStylesheet()
    content = request.json['content']
    # TODO: need to validate the content is actually css/less
    if len(content) > current_app.config['MAX_STYLESHEET_SIZE']:
        abort( 400 )
    if stylesheet.CurrentContent() != content:
        stylesheet.SetContent( content )
    return "OK"
