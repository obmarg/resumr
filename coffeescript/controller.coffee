define(
  [ 'layouts/sectionOverview', 'layouts/editor'
    'models/section', 'models/stylesheet',
    'collections/sectionList', 'views/sectionListView', 'views/sectionItemView',
    'views/sectionEditor', 'views/sectionEditorPreview', 'collections/sectionHistory',
    'views/sectionHistoryView', 'views/stylesheetEditor', 'views/editorTitlebar',
    'utils/styler'
  ],
  ( SectionOverviewLayout, EditorLayout
    Section, Stylesheet,
    SectionList, SectionListView, SectionItemView,
    SectionEditor, SectionEditorPreview, SectionHistory,
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

      sectionEditor: (section) ->
        # Not actually a view function, just used by the sectionNew & sectionEdit
        # view functions
        layout = new EditorLayout()
        @page.show(layout)

        preview = new SectionEditorPreview
        layout.right.show(preview)

        editor = new SectionEditor( model: section )
        layout.left.show( editor )
        editor.createEditor()

        titlebar = new EditorTitlebar(
          title: editor.getTitlebarText()
          isNew: section.isNew()
          namePlaceholder: 'Section Name'
        )
        layout.titlebar.show( titlebar )

        editor.bindTo( titlebar, 'save', editor.doSave )
        editor.bindTo( titlebar, 'cancel', editor.doCancel )
        editor.bindTo( titlebar, 'changename', editor.doChangeName )
        layout.bindTo( editor, 'error', layout.setError )
        return [ editor, titlebar ]

      sectionNew: (name) ->
        [editor, titlebar] = @sectionEditor(new Section)
        @newSectionBinding = editor.bindTo(
          editor, 'saved', (model) =>
            # Add the new model to the collection
            @sectionList.add( model )

            # Trigger a pagechange event and change the titlebar & URL
            @vent.trigger( 'changepage', 'sectionEdit' )
            titlebar.options.title = editor.getTitlebarText()
            titlebar.options.isNew = false
            titlebar.render()
            name = model.get( 'name' )
            Backbone.history.navigate(
              "section/#{name}/edit",
              replace: true
            )
            
            # Un-bind the event
            editor.unbindFrom( @newSectionBinding )
            @newSectionBinding = undefined
        )
        @vent.trigger( 'changepage', 'sectionNew' )

      sectionEdit: (name) ->
        @sectionFetch.then( =>
          # After the sections have been fetched,
          # set up the view
          section = @sectionList.get(name)
          @sectionEditor(section)
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
