define( 
  [ 'views/sectionItemView' ],
  ( SectionItemView ) ->
    class SectionListView extends Backbone.Marionette.CollectionView
      itemView: SectionItemView 
      
      initialize: () ->
        @bindTo( this, 'itemview:moveUp', @itemMoveUp )
        @bindTo( this, 'itemview:moveDown', @itemMoveDown )

      itemMoveUp: (item) ->
        model = item.model
        currentIndex = @collection.indexOf( model )
        if currentIndex != 0
          @collection.remove( model )
          @collection.add( model, at: currentIndex - 1 )
          @render()

      itemMoveDown: (item) ->
        model = item.model
        currentIndex = @collection.indexOf( model )
        newIndex = currentIndex + 1
        if newIndex < @collection.length 
          @collection.remove( model )
          @collection.add( model, at: newIndex )
          @render()
)
