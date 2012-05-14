define( 
  [ ],
  ( ) ->
    class SectionItemView extends Backbone.Marionette.ItemView
      template: '#section-item-template'

      events:
        'click .icon-remove' : 'onClickDelete'
        'click .icon-edit' : 'onClickEdit'
        # TODO: Marionette.View.triggers allows
        #       direct mapping of clicks to events
        #       So, use that for the clickUp & clickDown
        'click .icon-chevron-up' : 'onClickUp'
        'click .icon-chevron-down' : 'onClickDown'

      onClickDelete: () ->
        @model.destroy()

      onClickEdit: () ->
        name = @model.cid
        Backbone.history.navigate(
          "section/#{name}/edit"
          trigger: true
        )

      onClickUp: () ->
        @trigger( 'moveUp', @ )

      onClickDown: () ->
        @trigger( 'moveDown', @ )
)
