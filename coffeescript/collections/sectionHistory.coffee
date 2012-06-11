define(
  [ 'models/section' ],
  ( Section ) ->
    class SectionHistory extends Backbone.Collection
      model: Section

      initialize: ->
        
      doSetup: ( name, head ) ->
        @url = "api/sections/{#name}/history"
        @add(
          name: head.get( 'name' )
          content: head.get( 'content' )
        )

)
