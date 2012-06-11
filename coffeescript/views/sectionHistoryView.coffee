define(
  [ 'views/sectionHistoryItemView' ],
  ( SectionHistoryItemView ) ->
    class SectionHistoryView extends Backbone.Marionette.CollectionView
      itemView: SectionHistoryItemView
)
