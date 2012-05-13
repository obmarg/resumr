define( 
  [ ],
  ( ) ->
    class SectionItemView extends Backbone.Marionette.ItemView
      template: '#section-item-template'

      events:
        'click .icon-remove' : 'onClickDelete'
        'click .icon-edit' : 'onClickEdit'

      onClickDelete: () ->
        @model.destroy()

      onClickEdit: () ->
        name = @model.cid
        Backbone.history.navigate("section/#{name}/edit")
)
