define [ ], ( ) ->
  class SectionOverview extends Backbone.Marionette.Layout
    template: '#section-overview-template'
    regions:
      sidebar: '#sidebar'
      content: '#content'
