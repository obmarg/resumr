define(
  [ 'router', 'controller', 'requests' ],
  ( Router, Controller, InitRequests ) ->
    app = new Backbone.Marionette.Application()

    app.addInitializer( (options) ->
      controller = new Controller(@page,@vent)
      @router = new Router( controller: controller )
      Backbone.history.start()
    )

    app.addInitializer( InitRequests )

    app.addRegions(
      page: '#page'
    )

    # Register for changepage events, and update the titleBar
    app.vent.on( 'changepage', (pageName) ->
      # First, remove all active links from nav bar
      $( '#nav-left > li' ).removeClass( 'active' )
      if pageName == 'sectionOverview'
        $( '#overallNav' ).addClass( 'active' )
      else if pageName == 'sectionNew'
        $( '#newNav' ).addClass( 'active' )
    )

    return app
)
