define( 
  [ 'Pagedown' ],
  ( Pagedown ) ->
    class SectionEditor extends Backbone.Marionette.ItemView
      template: '#section-editor-template'

      events:
        'click #saveButton' : 'doSave' 
        'click #cancelButton' : 'doCancel'

      initialize: ->
        @editor = null

      serializeData: ->
        return item: @model.toJSON(), isNew: @model.isNew()

      createEditor: ->
        if @editor?
          return
        converter = new Pagedown.Converter()
        @editor = new Pagedown.Editor( converter )
        @editor.run()

      doSave: ->
        @model.save( 
          { content: $( '#wmd-input' ).val() },
          { success: => @vent.trigger( 'saved' ) }
        )
        # TODO: Move back to index?

      doCancel: ->
        $( '#wmd-input' ).val( @model.get( 'content' ) )
        @editor.refreshPreview()
        # TODO: Move back to index?
)
