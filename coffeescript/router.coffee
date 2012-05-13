define [  ], ( ) ->
  class AppRouter extends Backbone.Marionette.AppRouter
    appRoutes:
      '' : 'sectionOverview'
      'section/:name/edit' : 'sectionEdit'
