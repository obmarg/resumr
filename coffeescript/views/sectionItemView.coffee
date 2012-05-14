define( 
  [ 'Pagedown' ],
  ( Pagedown ) ->
    class SectionItemView extends Backbone.Marionette.ItemView
      template: '#section-item-template'

      events:
        'click .icon-remove' : 'onClickDelete'
        'click .icon-edit' : 'onClickEdit'

      triggers:
        'click .icon-chevron-up' : 'moveUp'
        'click .icon-chevron-down' : 'moveDown'

      initialize: ->
        @converter = Pagedown.getSanitizingConverter();

      serializeData: () ->
        return content: @converter.makeHtml( 
          @model.get( 'content' ) 
        )
        
      onClickDelete: () ->
        @model.destroy()

      onClickEdit: () ->
        name = @model.cid
        Backbone.history.navigate(
          "section/#{name}/edit"
          trigger: true
        )
)
