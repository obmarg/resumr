define [ ], ( ) ->
  class Section extends Backbone.Model
    defaults:
      content: ''

    urlRoot: 'api/sections'
    idAttribute: 'name'
    # TODO: Write validation function 
  
  return Section
