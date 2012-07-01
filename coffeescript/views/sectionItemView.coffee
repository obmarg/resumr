define( 
  [ 'Pagedown' ],
  ( Pagedown ) ->
    class SectionItemView extends Backbone.Marionette.ItemView
      template: '#section-item-template'

      events:
        'click .icon-remove' : 'onClickDelete'
        'click .icon-edit' : 'onClickEdit'
        'click .icon-list' : 'onClickHistory'

      triggers:
        'click .icon-chevron-up' : 'moveUp'
        'click .icon-chevron-down' : 'moveDown'

      initialize: ->
        @converter = Pagedown.getSanitizingConverter()
        if @model?
          @bindTo( @model, 'change', @render, @ )

      serializeData: () ->
        name: @model.get( 'name' )
        content: @converter.makeHtml( @model.get( 'content' ) )
        
      onClickDelete: () ->
        @model.destroy()

      onClickEdit: () ->
        name = @model.get( 'name' )
        Backbone.history.navigate(
          "section/#{name}/edit"
          trigger: true
        )

      onClickHistory: () ->
        name = @model.get( 'name' )
        Backbone.history.navigate(
          "section/#{name}/history"
          trigger: true
        )
)
