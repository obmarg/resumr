Feature: Render CV
    In order to print out my CV
    As a user
    I want to view a plain HTML render of the CV

    Background:
        
    Scenario: Open render page
        Given the following sections:
            | name      | content       |
            | no1       | ### textify   |
            | no2       | sometext      |
        And I have a stylesheet containing "h3 {text-align:right;}"
        And I am on the main page
        When I click on #renderLink
        Then I should be on the render page
        And I should see the following rendered sections
            | name      | content       |
            | no1       | textify       |
            | no2       | sometext      |
        And the style tag #stylesheet should contain "h3 {text-align:right;}"
        
    #TODO: Would be nice to test computed styles out here...
