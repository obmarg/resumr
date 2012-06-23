define(
  [ 'router', 'controller', 'requests' ],
  ( Router, Controller, InitRequests ) ->
    app = new Backbone.Marionette.Application()

    app.addInitializer( (options) ->
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
