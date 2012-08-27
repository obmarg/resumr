define( 
  [ 'Pagedown' ],
  ( Pagedown ) ->
    class SectionEditor extends Backbone.Marionette.ItemView
      template: '#section-editor-template'

      initialize: ->
        @editor = null

      serializeData: ->
        return item: @model.toJSON()

      getTitlebarText: ->
        if @model.isNew()
          return "New Section"
        else
          return "Editing Section \"#{@model.id}\""

      createEditor: ->
        if @editor?
          return
        converter = new Pagedown.getSanitizingConverter()
        @editor = new Pagedown.Editor( converter )
        @editor.run()

      doChangeName: (name) ->
        @name = name

      doSave: ->
        data = content: $( '#wmd-input' ).val()
        if @model.isNew()
          data.newName = @name
        else if data.content == @model.get( 'content' )
          # Don't bother saving if nothing has actually changed
          return
        @model.save( data,
          success: =>
            @trigger( 'saved', @model )
          error: (model, response) =>
            # Display the error to the user
            # TODO: This doesn't seem to handle server errors as well as it should
            @trigger('error', response)
        )

      doCancel: ->
        $( '#wmd-input' ).val( @model.get( 'content' ) )
        @editor.refreshPreview()
)
