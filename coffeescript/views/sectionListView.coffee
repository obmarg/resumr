define(
  [ 'views/sectionItemView' ],
  ( SectionItemView ) ->
    class SectionListView extends Backbone.Marionette.CollectionView
      itemView: SectionItemView

      initialize: ->
        @bindTo( this, 'itemview:moveUp', @itemMoveUp )
        @bindTo( this, 'itemview:moveDown', @itemMoveDown )
        @options.showTools ?= true

      itemViewOptions: ->
        showTools: @options.showTools

      itemMoveUp: (item) ->
        model = item.model
        currentIndex = @collection.indexOf( model )
        if currentIndex != 0
          other = @collection.at( currentIndex - 1 )
          currentPos = model.get( 'pos' )
          model.set( 'pos', currentPos - 1 )
          other.set( 'pos', currentPos )
          model.save()
          other.save()
          @collection.sort()

      itemMoveDown: (item) ->
        model = item.model
        currentIndex = @collection.indexOf( model )
        if currentIndex < @collection.length
          other = @collection.at( currentIndex + 1 )
          currentPos = model.get( 'pos' )
          model.set( 'pos', currentPos + 1 )
          other.set( 'pos', currentPos )
          model.save()
          other.save()
          @collection.sort()

)
