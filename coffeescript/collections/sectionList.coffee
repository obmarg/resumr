define( [ 'models/section' ], ( Section ) ->
  class SectionList extends Backbone.Collection
    url: 'api/sections'
    model: Section
)
