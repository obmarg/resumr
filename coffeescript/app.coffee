define(
  [ 'router', 'controller' ],
  ( Router, Controller ) ->
    app = new Backbone.Marionette.Application()

    app.addInitializer( (options) ->
      controller = new Controller(@page,@vent)
      @router = new Router( controller: controller )
      Backbone.history.start()
    )

    app.addInitializer( ->
      amplify.request.define( 'SelectHistoryItem', 'ajax',
        url: '/api/sections/{name}/history/select/{id}'
        type: 'POST'
      )
    )

    app.addRegions(
      page: '#page'
    )

    # Register for changepage events, and update the titleBar
    app.vent.on( 'changepage', (pageName) ->
      # First, remove all active links from nav bar
      $( '#nav-left > li' ).removeClass( 'active' )
      # Then add an active link to the appropriate page
      $( "##{pageName}Nav" ).addClass( 'active' )
    )

    return app
)
