define [ ], ( ) ->
  class Section extends Backbone.Model
    defaults:
      content: ''

    urlRoot: 'api/sections'
    idAttribute: 'name'

    validate: ( attrs ) ->
      if @isNew() and not attrs.newName
        return {
          field: 'name'
          text: "Sections can't be saved without a name" 
        }
      if attrs.content.length < 1
        return {
          field: 'content'
          text: 'Fill in some content before saving'
        }
      return
  
  return Section
