define(
  [ 'router', 'controller', 'requests' ],
  ( Router, Controller, InitRequests ) ->
    app = new Backbone.Marionette.Application()

    app.addInitializer( (options) ->
      # TODO: Check if authed here.
      #       If not - then we want to redirect to /login
      #       For the sake of simplicity just now, I'm going to redirect
      #       to /login all the time
      window.location.href = '/login'
      controller = new Controller(this.page)
      this.router = new Router( controller: controller )
      Backbone.history.start()
    )

    app.addInitializer( InitRequests )

    app.addRegions(
      page: '#page'
    )

    return app
)
