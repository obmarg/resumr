require.config
  baseUrl: "js/"
  paths:
    Mustache: "libs/mustache/mustache-wrapper"
    Pagedown: "libs/Pagedown/pagedown-wrapper"

require [ 'app' ], ( app ) ->
  options = {
    # Something
  }

  app.start( options )
