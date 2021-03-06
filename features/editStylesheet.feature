Feature: Edit Stylesheet
    In order to make my CV look sweet
    As a user
    I want to edit it's stylesheet

    Background:
        Given the following sections:
            | name      | content       |
            | no1       | ### textify   |
            | no2       | sometext      |

    Scenario: Open stylesheet page
        Given I am on the main page
        When I click on #stylesheetLink
        Then I should be on the stylesheet page
        And I should see "" in #editor

    Scenario: Live preview on open stylesheet page
        Given I have a stylesheet containing "h3 {text-align:right;}"
        And I am on the main page
        When I click on #stylesheetLink
        Then I should be on the stylesheet page
        And I should see "h3 {text-align:right;}" in #editor
        And the style tag #stylesheetEditorPreviewCss should contain "#editorRightPane h3 {text-align:right;}"

    Scenario: Live preview after edit
        Given I am on the stylesheet page
        When I enter "h3 {text-align:right;}" in the stylesheet editor
        Then the style tag #stylesheetEditorPreviewCss should contain "#editorRightPane h3 {text-align:right;}"

    Scenario: Cancel editing
        Given I am on the stylesheet page
        And I enter "h3 { text-align: right; }" in the stylesheet editor
        When I click on #cancelButton
        Then I should be on the stylesheet page
        And I should see "" in #editor

    Scenario: Enter text then leave page
        Given I am on the stylesheet page
        And I enter "h3 { text-align: right; }" in the stylesheet editor
        When I click on #sectionListLink
        And I click on #stylesheetLink
        Then I should be on the stylesheet page
        And I should see "" in #editor

    Scenario: Submit form
        Given I am on the stylesheet page
        And I enter "h3 { text-align: right; }" in the stylesheet editor
        When I click on #saveButton
        Then I should be on the stylesheet page
        And I should see "h3 { text-align: right; }" in #editor

    Scenario: Submit form, nav away then nav back
        Given I am on the stylesheet page
        And I enter "h3 { .opaque; }" in the stylesheet editor
        And I click on #saveButton
        And I click on #sectionListLink
        When I click on #stylesheetLink
        Then I should see "h3 { .opaque; }" in #editor

    Scenario: Submit then view index
        Given I am on the stylesheet page
        And I enter "h3 {text-align:right;}" in the stylesheet editor
        When I click on #saveButton
        And I view the main page
        Then the style tag #stylesheet should contain ".styleParent h3 {text-align:right;}"

    #TODO: Would be nice to actually verify computed styles etc...
