define(
  [ 'models/sectionHistoryItem' ],
  ( SectionHistoryItem ) ->
    class SectionHistory extends Backbone.Collection
      model: SectionHistoryItem

      initialize: ->
        
      doSetup: ( name, head ) ->
        @url = "api/sections/#{name}/history"
        @add(
          id: 0
          name: head.get( 'name' )
          content: head.get( 'content' )
        )
        @fetch()
)
