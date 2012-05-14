define( 
  [ 'Pagedown' ],
  ( Pagedown ) ->
    class SectionEditor extends Backbone.Marionette.ItemView
      template: '#section-editor-template'

      events:
        'change #wmd-input' : 'onChange'
        'click #wmd-undo-button' : 'onChange'
        'click #wmd-redo-button' : 'onChange'

      initialize: ->
        @editor = null

      createEditor: ->
        if @editor?
          return
        converter = new Pagedown.Converter()
        @editor = new Pagedown.Editor( converter )
        @editor.run()

      onChange: ->
        @model.set( 'content', $( '#wmd-input' ).val() )
)
