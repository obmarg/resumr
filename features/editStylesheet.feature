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

    Scenario: Live preview
        Given I am on the stylesheet page
        When I enter "h3 { text-align:right; }" in the stylesheet editor
        Then the style tag should contain "#editorRightPane h3 { text-align:right; }"

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

    Scenario: Validation failure
        Given I am on the stylesheet page
        And I enter "h3 { " in the stylesheet editor
        When I click on #saveButton
        Then I should see an error "invalid css" 

    Scenario: Submit then view index
        Given I am on the stylesheet page
        And I enter "h3 { text-align: right; }" in the stylesheet editor
        When I click on #saveButton
        And I view the main page
        Then I should see "textify" right aligned in #section-no1
