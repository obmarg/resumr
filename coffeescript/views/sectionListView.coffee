define( 
  [ 'views/sectionItemView' ],
  ( SectionItemView ) ->
    class SectionListView extends Backbone.Marionette.CollectionView
      itemView: SectionItemView 
)
