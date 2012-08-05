define [ ], ( ) ->
  class Stylesheet extends Backbone.Model
    isNew: -> return false

    url: -> return "api/stylesheet"

  return Stylesheet
