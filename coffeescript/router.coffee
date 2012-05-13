define [  ], ( ) ->
  AppRouter = Backbone.Router.extend(
    routes:
      "": "main"

    initialize: ->
      @currentView = null
      events.on( 'closeView', @onCloseEvent, @ )

    main: (id) ->
      @currentView = null

    changeView: (newView) ->
      @closeView()
      $("#content").html ""
      $("#content").append newView.el
      newView.render()
      @currentView = newView

    onCloseEvent: ->
      @closeView()
      @navigate( '/' )
    
    closeView: ->
      @clearSidebar()
      if @currentView isnt null
        @currentView.onClose()
        @currentView = null
  )
  initialize = ->
    app_router = new AppRouter
    Backbone.history.start()

  initialize: initialize
