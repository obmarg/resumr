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

        @sectionFetch = $.Deferred()
        @sectionList = new SectionList()
        @sectionList.fetch(
          success: => @sectionFetch.resolve()
          failure: => @sectionFetch.reject()
        )

      sectionOverview: ->
        layout = new SectionOverviewLayout()
        layout.render()
        @page.show( layout )
        
        sectionListView = new SectionListView( 
          collection: @sectionList 
        )
        layout.content.show( sectionListView )

      sectionNew: (name) ->
        layout = new SectionEditor( model: new Section )
        @newSectionBinding = layout.bindTo(
          layout, 'saved', (model) =>
            @sectionList.add( model )
            layout.unbindFrom( @newSectionBinding )
            @newSectionBinding = undefined
        )
        @page.show( layout )
        layout.createEditor()

      sectionEdit: (name) ->
        @sectionFetch.then( =>
          # After the sections have been fetched,
          # set up the view
          section = @sectionList.find( (item) -> 
            item.get( 'name' ) == name
          )
          layout = new SectionEditor( model: section )
          @page.show( layout )
          layout.createEditor()
        )

       
    return Controller
)
