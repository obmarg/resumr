define( 
  [ 'router', 'layouts/sectionOverview', 'models/section', 'collections/sectionList', 'views/sectionListView', 'views/sectionItemView' ], 
  ( Router, SectionOverviewLayout, Section, SectionList, SectionListView, SectionItemView ) ->
    app = new Backbone.Marionette.Application()

    app.addInitializer( (options) ->
      # TODO: Do something with router
      # TODO: call backbone history start?
      layout = new SectionOverviewLayout()
      layout.render()
      app.page.show( layout )

      # Load Temporary test data
      content1 = $( '#tempData1' ).html()
      content2 = $( '#tempData2' ).html()

      section1 = new Section( content: content1 )
      section2 = new Section( content: content2 )

      sectionList = new SectionList([ section1, section2 ])

      sectionListView = new SectionListView( collection: sectionList )
      layout.content.show( sectionListView )
    )

    app.addRegions(
      page: '#page'
    )
    
    return app
)
