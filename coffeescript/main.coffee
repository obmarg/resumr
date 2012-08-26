require.config
  baseUrl: "static/js/"
  paths:
    Mustache: "libs/mustache/mustache-wrapper"
    Pagedown: "libs/Pagedown/pagedown-wrapper"
    CodeMirror: "libs/CodeMirror/codemirror-wrapper"

require [ 'app' ], ( app ) ->
  options = {
    # Something
  }

  app.start( options )
