define(
  [],
  () ->
    class EditorTitlebar extends Backbone.Marionette.ItemView
      template: '#editor-titlebar-template'

      triggers:
        'click #saveButton' : 'save'
        'click #cancelButton' : 'cancel'

      serializeData: ->
        title: @options.title
        isNew: @options.isNew ? false
        namePlaceholder: @options.namePlaceholder ? ""
)
