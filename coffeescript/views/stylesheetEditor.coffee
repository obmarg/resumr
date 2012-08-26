define(
  [ 'CodeMirror' ],
  ( CodeMirror ) ->
    class StylesheetEditor extends Backbone.Marionette.ItemView
      template: '#stylesheet-editor-template'

      updateTimeout: 500

      events:
        'change #stylesheetEditor': 'onBaseChange'

      initialize: ->

      createEditor: ->
        # This should be called after we've been attached
        # to the DOM
        textArea = @$el.find( '#stylesheetEditor' )[0]
        @codeMirror = CodeMirror.fromTextArea(textArea,
          lineWrapping: true
          onChange: => @onChange()
        )
        @codeMirror.setValue( @model.get('content') )
        @updatePreview()

      onBaseChange: ->
        # Called whenever the base html text area is changed.
        # Usually we wouldn't care about this, but it's
        # needed for some tests
        @codeMirror.setValue( $( '#stylesheetEditor' ).val() )
        
        # Since this is just used for tests, skip the usual wait time,
        # and update the preview directly
        @updatePreview()

      onChange: ->
        # Called by code mirror when the contents change
        if @updateTimeoutId?
          clearTimeout( @updateTimeoutId )
        @updateTimeoutId = setTimeout( =>
            @updatePreview()
          , @updateTimeout
        )

      updatePreview: ->
        @trigger( 'change', @codeMirror.getValue() )

      doSave: ->
        @model.save( content: @codeMirror.getValue(),
          success: =>
            #TODO: potentially close the view or something?
          error: =>
            #TODO: Fire error event.
            #      For now, let's check what happens by default.
            #      Could be an event fires automatically...
        )

      doCancel: ->
        @codeMirror.setValue( @model.get('content') )
)
