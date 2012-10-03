
import json
import re
from flask import Blueprint, abort, request
from db import ContentNotFound
from utils.viewutils import GetDoc
from utils.markdownutils import ValidateMarkdown

app = Blueprint('section_api', __name__)

SECTION_NAME_REGEXP = re.compile(r'^\w+$')

class InvalidSectionName(Exception):
    pass


@app.route('', methods=['GET'])
def ListSections():
    ''' Lists the current sections including order '''
    d = GetDoc()
    sections = [ {
                'name': s.name,
                'pos': i,
                'content': s.CurrentContent()
                } for i, s in d.CurrentSections() ]
    # TODO: Maybe make this return an object
    #       Seem to remember some security warning for
    #       returning lists
    #       Probably want to use jsonify (?) as well
    return json.dumps( sections )


@app.route('/<name>', methods=['GET'])
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


@app.route('', methods=['POST'])
def AddSection():
    '''
    Adds a section.
    '''
    d = GetDoc()
    data = request.json
    try:
        name = data[ 'newName' ]
    except KeyError:
        # We check data['name'] for the sake of component tests.
        # The javascript clientside should send via newName,
        # as otherwise it mistakes the new section for an existing
        # one, and attempts to PUT
            name = data[ 'name' ]
    if not SECTION_NAME_REGEXP.match(name):
        raise InvalidSectionName(name)
    content = data['content']
    ValidateMarkdown(content)
    s = d.AddSection(name, content)
    return json.dumps({
        'name': s.name,
        'content': content,
        'pos': s.GetPosition()
        })


@app.route('/<name>', methods=['PUT'])
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
    return "OK"


@app.route('/<name>', methods=['DELETE'])
def RemoveSection(name):
    '''
    Removes a section

    Args:
        name    The name of the section to remove
    '''
    d = GetDoc()
    d.RemoveSection( name )
    return "OK"


@app.route('/<name>/history', methods=['GET'])
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
        data.append( { 'id': i, 'content': d } )
    return json.dumps( data )


@app.route(
    '/<name>/history/select/<int:historyId>',
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

