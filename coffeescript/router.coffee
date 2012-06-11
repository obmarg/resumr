define [  ], ( ) ->
  class AppRouter extends Backbone.Marionette.AppRouter
    appRoutes:
      '' : 'sectionOverview'
      'newSection' : 'sectionNew'
      'section/:name/edit' : 'sectionEdit'
      'section/:name/history' : 'sectionHistory'
