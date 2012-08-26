define( 
  [ ],
  ( ) ->
    class EditorLayout extends Backbone.Marionette.Layout
      template: '#editor-layout-template'

      regions: {
        titlebar: '#editorTitlebar'
        left: '#editorLeftPane'
        right: '#editorRightPane'
      }

      setError: (error) ->
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
)
