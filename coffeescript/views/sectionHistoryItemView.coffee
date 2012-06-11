define(
  [ 'Pagedown' ],
  ( Pagedown ) ->
    class SectionHistoryItemView extends Backbone.Marionette.ItemView
      template: '#section-history-item-template'

      initialize: ->
        # TODO: Would be good to only have one converter
        #       per history view, rather than per item
        @converter = Pagedown.getSanitizingConverter()

      serializeData: () ->
        return content: @converter.makeHtml(
          @model.get( 'content' )
        )
)
