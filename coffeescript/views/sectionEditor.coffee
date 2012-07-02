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

      setError: ( error ) ->
        # TODO: Would be good to highlight the offending field
        # TODO: Also look into replacing this clumsy alert with
        #       a tool tip on the offending field or something?
        if error.text?
          $( '#editorError' ).text( error.text ).addClass( 'opaque' )
          setTimeout(
            -> $( '#editorError' ).removeClass( 'opaque' ),
            3000
          )
        #TODO: Make this handle server errors as well?

      doSave: ->
        data =
          content: $( '#wmd-input' ).val()
        isNew = false
        if @model.isNew()
          data.newName = $( '#sectionName' ).val()
          isNew = true
        else if data.content == @model.get( 'content' )
          # Don't bother saving if nothing has actually changed
          return
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
          error: (model, response) =>
            # Display the error to the user
            @setError( response )
        )

      doCancel: ->
        $( '#wmd-input' ).val( @model.get( 'content' ) )
        @editor.refreshPreview()
)
