define( [ 'models/section' ], ( Section ) ->
  class SectionList extends Backbone.Collection
    url: 'api/sections'
    model: Section

    comparator: (l,r) ->
      lpos = l.get( 'pos' )
      rpos = r.get( 'pos' )
      if lpos < rpos
        return -1
      if lpos > rpos
        return 1
      return 0
)
