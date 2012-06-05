define [ ], ( ) ->
  class Section extends Backbone.Model
    defaults:
      content: ''

    urlRoot: 'api/sections'
    idAttribute: 'name'

    validate: ->
      if @isNew() and not @get( 'newName' )
        return {
          field: 'name'
          text: "Sections can't be saved without a name" 
        }
      if @get( 'content' ).length < 1
        return {
          field: 'content'
          text: 'Fill in some content before saving'
        }
      return
  
  return Section
