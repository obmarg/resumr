define(
  [],
  () ->
    class EditorTitlebar extends Backbone.Marionette.ItemView
      template: '#editor-titlebar-template'

      events:
        'change #nameField' : 'triggerChangeName'

      triggers:
        'click #saveButton' : 'save'
        'click #cancelButton' : 'cancel'

      triggerChangeName: ->
        @trigger('changename', $('#nameField').val())

      serializeData: ->
        title: @options.title
        isNew: @options.isNew ? false
        namePlaceholder: @options.namePlaceholder ? ""
)
