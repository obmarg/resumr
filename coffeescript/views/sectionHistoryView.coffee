define(
  [ 'views/sectionHistoryItemView' ],
  ( SectionHistoryItemView ) ->
    class SectionHistoryView extends Backbone.Marionette.CollectionView
      itemView: SectionHistoryItemView
      
      initialize: ->
        @bindTo( this, 'itemview:onSelectSection', @onSelectSection )

      onSelectSection: ( itemView ) ->
        historyId = itemView.model.id
        amplify.request(
          'SelectHistoryItem',
          { name: @collection.name, id: historyId },
          => @trigger( 'doClose' )
        )
)
