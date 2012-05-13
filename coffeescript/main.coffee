require.config
  baseUrl: "js/"
  paths:
    Mustache: "libs/mustache/mustache-wrapper"

require [ 'app' ], ( app ) ->
  options = {
    # Something
  }

  app.start( options )
