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
        And I should see "" in #stylesheetEditor

    Scenario: Live preview
        Given I am on the stylesheet page
        When I enter "h3 { text-align: right; }" in #stylesheetEdit
        Then I should see "textify" right aligned in #stylesheetPreview

    Scenario: Cancel editing
        Given I am on the stylesheet page
        When I click on #cancelButton
        Then I should be on the stylesheet page
        And I should see "" in #stylesheetEdit

    Scenario: Submit form
        Given I am on the stylesheet page
        And I enter "h3 { text-align: right; }" in #stylesheetEdit
        When I click on #saveButton
        Then I should be on the stylesheet page
        And I should see "h3 { text-align: right; }" in #stylesheetEdit

    Scenario: Validation failure
        Given I am on the stylesheet page
        And I enter "h3 { " in #stylesheetEdit
        When I click on #saveButton
        Then I should see an error "invalid css" 

    Scenario: Submit then view index
        Given I am on the stylesheet page
        And I enter "h3 { text-align: right; }" in #stylesheetEdit
        When I click on #saveButton
        And I view the main page
        Then I should see "textify" right aligned in #section-no1
