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
        if @model.isNew()
          $( '#sectionName' ).focus()
        else:
          $( '#wmd-input' ).focus()

      doSave: ->
        data =
          content: $( '#wmd-input' ).val()
        isNew = false
        if @model.isNew()
          data.newName = $( '#sectionName' ).val()
          isNew = true
        @model.save( data,
          success: =>
            @trigger( 'saved', @model )
            if isNew
              # Destroy the editor and re-render
              # There might be a better way to do this but
              # for now this'll do.
              @editor = undefined
              @render().then( => @createEditor() )
              name = @model.get( 'name' )
              # Update the URL to the editing URL
              # I'm not 100% happy with doing things this way,
              # maybe look into alternatives sometime
              Backbone.history.navigate(
                "section/#{name}/edit",
                replace: true
              )
        )

      doCancel: ->
        $( '#wmd-input' ).val( @model.get( 'content' ) )
        @editor.refreshPreview()
)
