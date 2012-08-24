define( 
  [ ],
  ( ) ->
    class EditorLayout extends Backbone.Marionette.Layout
      template: '#editor-layout-template'

      regions: {
        toolbar: '#editorToolbar'
        errorPane: '#editorErrorContainer'
        left: '#editorLeftPane'
        right: '#editorRightPane'
      }
)
