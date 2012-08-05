define(
  [ 'CodeMirror' ],
  ( CodeMirror ) ->
    class StylesheetEditor extends Backbone.Marionette.ItemView
      template: '#stylesheet-editor-template'

      events:
        'click #saveButton' : 'doSave'
        'click #cancelButton' : 'doCancel'

      initialize: ->

      onRender: ->
        textArea = @$el.find( '#stylesheetEditor' )[0]
        @codeMirror = CodeMirror.fromTextArea(textArea,
          lineWrapping: true
        )

      doSave: ->

      doCancel: ->

)
