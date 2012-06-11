define(
  [ 'views/sectionHistoryItem' ],
  ( SectionHistoryItemView ) ->
    class SectionHistoryView extends Backbone.Marionette.CollectionView
      itemView: SectionHistoryItemView
)
