define(
  [ 'CodeMirror' ],
  ( CodeMirror ) ->
    class StylesheetEditor extends Backbone.Marionette.ItemView
      template: '#stylesheet-editor-template'

      events:
        'change #stylesheetEditor': 'onBaseChange'

      initialize: ->

      createEditor: ->
        # This should be called after we've been attached
        # to the DOM
        textArea = @$el.find( '#stylesheetEditor' )[0]
        @codeMirror = CodeMirror.fromTextArea(textArea,
          lineWrapping: true
        )
        @codeMirror.setValue( @model.get('content') )

      onBaseChange: ->
        # Called whenever the base html text area is changed.
        # Usually we wouldn't care about this, but it's
        # needed for some tests
        @codeMirror.setValue( $( '#stylesheetEditor' ).val() )

      doSave: ->
        @model.save( content: @codeMirror.getValue(),
          success: =>
            #TODO: potentially close the view or something?
          error: =>
            #TODO: display error message.
            #       But for now, let's check what else happens
        )

      doCancel: ->
        @codeMirror.setValue( @model.get('content') )
)
