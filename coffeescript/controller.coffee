define( 
  [ 'layouts/sectionOverview', 'models/section', 'collections/sectionList', 'views/sectionListView', 'views/sectionItemView', 'views/sectionEditor' ],
  ( SectionOverviewLayout, Section, SectionList, SectionListView, SectionItemView, SectionEditor ) ->
    class Controller 
      constructor: (@page) ->
        # Load Temporary test data
        content1 = $( '#tempData1' ).html()
        content2 = $( '#tempData2' ).html()

        section1 = new Section( content: content1 )
        section2 = new Section( content: content2 )

        @sectionList = new SectionList([ section1, section2 ])

      sectionOverview: ->
        layout = new SectionOverviewLayout()
        layout.render()
        @page.show( layout )
        
        sectionListView = new SectionListView( 
          collection: @sectionList 
        )
        layout.content.show( sectionListView )

      sectionEdit: (name) ->
        section = @sectionList.find( (item) -> 
          item.cid == name
        )
        layout = new SectionEditor( model: section )
        @page.show( layout )
        layout.createEditor()

    return Controller
)
