require.config
  baseUrl: "/static/"
  paths:
    Mustache: "libs/mustache/mustache-wrapper"

require [ 
  "app",
], (App) ->
  App.initialize()
