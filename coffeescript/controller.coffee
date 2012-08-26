define(
  [ 'layouts/sectionOverview', 'layouts/editor'
    'models/section', 'models/stylesheet',
    'collections/sectionList', 'views/sectionListView', 'views/sectionItemView',
    'views/sectionEditor', 'collections/sectionHistory',
    'views/sectionHistoryView', 'views/stylesheetEditor', 'views/editorTitlebar',
    'utils/styler'
  ],
  ( SectionOverviewLayout, EditorLayout
    Section, Stylesheet,
    SectionList, SectionListView, SectionItemView,
    SectionEditor, SectionHistory,
    SectionHistoryView, StylesheetEditor, EditorTitlebar,
    Styler
  ) ->
    class Controller
      constructor: (@page, @vent) ->
        @sectionList = new SectionList()
        @sectionFetch = @sectionList.fetch()
        @stylesheet = new Stylesheet()
        @stylesheetFetch = @stylesheet.fetch()
        @styler = new Styler('stylesheet', '.styleParent')
        @stylesheet.on('change', => @styler.update(@stylesheet.get('content')))
        @stylesheet.on('reset', => @styler.update(@stylesheet.get('content')))

      sectionOverview: ->
        layout = new SectionOverviewLayout()
        layout.render()
        @page.show( layout )

        sectionListView = new SectionListView(
          collection: @sectionList
          className: 'styleParent'
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
          # TODO: switch the section editor to use the editor layout
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
          layout = new EditorLayout()
          @page.show( layout )

          previewStyler = new Styler(
            'stylesheetEditorPreviewCss', '#editorRightPane'
          )

          editor = new StylesheetEditor( model: @stylesheet )
          layout.left.show( editor )
          editor.bindTo( editor, 'change', previewStyler.update, previewStyler )
          editor.createEditor()
          preview = new SectionListView(
            collection: @sectionList
            showTools: false
          )
          layout.right.show( preview )
          titlebar = new EditorTitlebar(
            title: "Editing Stylesheet"
          )
          layout.titlebar.show( titlebar )

          editor.bindTo( titlebar, 'save', editor.doSave )
          editor.bindTo( titlebar, 'cancel', editor.doCancel )
          layout.bindTo( editor, 'error', layout.setError )

          @vent.trigger( 'changepage', 'stylesheetEdit' )
        )

    return Controller
)
