define(
  [ 'layouts/sectionOverview', 'models/section', 'models/stylesheet',
    'collections/sectionList', 'views/sectionListView', 'views/sectionItemView',
    'views/sectionEditor', 'collections/sectionHistory',
    'views/sectionHistoryView', 'views/stylesheetEditor'
  ],
  ( SectionOverviewLayout, Section, Stylesheet,
    SectionList, SectionListView, SectionItemView,
    SectionEditor, SectionHistory,
    SectionHistoryView, StylesheetEditorView
  ) ->
    class Controller
      constructor: (@page, @vent) ->
        # Load Temporary test data
        content1 = $( '#tempData1' ).html()
        content2 = $( '#tempData2' ).html()

        section1 = new Section( content: content1 )
        section2 = new Section( content: content2 )

        @sectionList = new SectionList()
        @sectionFetch = @sectionList.fetch()
        @stylesheet = new Stylesheet()
        @stylesheetFetch = @stylesheet.fetch()

      sectionOverview: ->
        layout = new SectionOverviewLayout()
        layout.render()
        @page.show( layout )

        sectionListView = new SectionListView(
          collection: @sectionList
        )
        layout.content.show( sectionListView )
        @vent.trigger( 'changepage', 'sectionOverview' )

      sectionNew: (name) ->
        layout = new SectionEditor( model: new Section )
        @newSectionBinding = layout.bindTo(
          layout, 'saved', (model) =>
            @sectionList.add( model )
            layout.unbindFrom( @newSectionBinding )
            @newSectionBinding = undefined
            @vent.trigger( 'changepage', 'sectionEdit' )
        )
        @page.show( layout )
        layout.createEditor()
        @vent.trigger( 'changepage', 'sectionNew' )

      sectionEdit: (name) ->
        @sectionFetch.then( =>
          # After the sections have been fetched,
          # set up the view
          # TODO: Replace this find with something simpler
          section = @sectionList.find( (item) ->
            item.get( 'name' ) == name
          )
          layout = new SectionEditor( model: section )
          @page.show( layout )
          layout.createEditor()
          @vent.trigger( 'changepage', 'sectionEdit' )
        )

      sectionHistory: (name) ->
        # Opens the section history view
        @sectionFetch.then( =>
          # After the sections have been fetched,
          # set up the view
          # TODO: Replace this find with something simpler
          section = @sectionList.find( (item) ->
            item.get( 'name' ) == name
          )
          history = new SectionHistory
          history.doSetup( name, section )
          layout = new SectionHistoryView( collection: history )
          @sectionHistoryBinding = layout.bindTo(
            layout, 'doClose', =>
              # TODO: Could be good to delay switching back till we've
              #       received this here fetch...?
              section.fetch()
              layout.unbindFrom( @sectionHistoryBinding )
              @sectionHistoryBinding = undefined
              Backbone.history.navigate( '', trigger: true )
          )
          @page.show( layout )
          @vent.trigger( 'changepage', 'sectionHistory' )
        )

      stylesheetEdit: ->
        # Opens the stylesheet editor
        @stylesheetFetch.then( =>
          layout = new StylesheetEditorView()
          @page.show( layout )
          @vent.trigger( 'changepage', 'stylesheetEdit' )
        )

    return Controller
)
