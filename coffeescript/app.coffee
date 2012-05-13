define( 
  [ 'router', 'controller' ], 
  ( Router, Controller ) ->
    app = new Backbone.Marionette.Application()

    app.addInitializer( (options) ->
      controller = new Controller(this.page)
      this.router = new Router( controller: controller )
      Backbone.history.start()
    )

    app.addRegions(
      page: '#page'
    )
    
    return app
)
