define [ ], ( ) ->
  Section = Backbone.Model.extend(
    defaults: 
      content: 'blah de blah'
      name: 'Something'
  )
  return Section
