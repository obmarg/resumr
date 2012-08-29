define [ ], ( ) ->
  class Section extends Backbone.Model
    defaults:
      content: ''

    urlRoot: 'api/sections'
    idAttribute: 'name'

    nameRegexp: /^\w+$/
    invalidContentRegexp: /<[^>]*>/

    validate: ( attrs ) ->
      if @isNew()
        if not attrs.newName
          return {
            field: 'name'
            text: "Sections can't be saved without a name" 
          }
        else if not attrs.newName.match(@nameRegexp)
          return {
            field: 'name'
            text: 'Names must not have spaces or punctuation'
          }
      if attrs.content.length < 1
        return {
          field: 'content'
          text: 'Fill in some content before saving'
        }
      else if attrs.content.match(@invalidContentRegexp)
        return {
          field: 'content'
          text: 'Content must not contain HTML tags'
        }
      return
  
  return Section
