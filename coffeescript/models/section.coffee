define [ ], ( ) ->
  Section = Backbone.Model.extend(
    defaults: 
      content: ''
    idAttribute: 'name'
    # TODO: Write validation function 
  )
  return Section
