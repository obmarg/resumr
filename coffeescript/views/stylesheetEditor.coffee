define(
  [],
  () ->
    class StylesheetEditor extends Backbone.Marionette.ItemView
      template: '#stylesheet-editor-template'

      events:
        'click #saveButton' : 'doSave'
        'click #cancelButton' : 'doCancel'

      initialize: ->


      doSave: ->

      doCancel: ->

)
