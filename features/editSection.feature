Feature: Edit Existing Section
    In order to fix some mistakes I made
    As a user
    I want to edit an existing section

    Scenario: Open edit section page
        Given the following sections:
            | name      | content       | 
            | no1       | textify       | 
        And I am on the edit section page for no1
        Then I should see "textify" in #wmd-input
        And I should see "textify" in the preview
        And I should see the edit section "no1" title 

    Scenario Outline: Edit the text and look at the preview
        Given the following sections:
            | name      | content       | 
            | no1       | textify       | 
        And I am on the edit section page for no1
        When I enter <text> in #wmd-input
        Then I should see <text> in the preview

        Examples:
            | text              |
            | hello world       |
            | something good    |
            | BRILLIANT!!!!     |

    Scenario: More complex text preview
        Given the following sections:
            | name      | content       | 
            | no1       | textify       | 
        And I am on the edit section page for no1
        When I type into #wmd-input:
            """
            Hello
            ===

            This is a great test

            * Here
            * Is
            * A
            * List
            """
        Then I should see "This is a great test" in the preview
        And I should see a list containing:
            | item  |
            | Here  |
            | Is    |
            | A     |
            | List  |
        And I should see an h1 element containing "Hello"

    Scenario: Cancelling my changes
        Given the following sections:
            | name      | content       | 
            | no1       | textify       | 
        And I am on the edit section page for no1
        When I enter "something" in #wmd-input
        Then I click on #cancelButton
        Then I should see "textify" in #wmd-input
        And I should see "textify" in the preview

    Scenario: Submit form (and stay on page)
        Given the following sections:
            | name      | content       | 
            | no1       | textify       | 
        And I am on the edit section page for no1
        And I have entered "An edit" in #wmd-input
        When I click on #saveButton
        Then I should be on the edit section page for no1
        And I should see the edit section "no1" title

    Scenario: Attempt to submit empty text
        Given the following sections:
            | name      | content       | 
            | no1       | textify       | 
        And I am on the edit section page for no1
        And I have entered "" in #wmd-input
        When I click on #saveButton
        Then I should be on the edit section page for no1
        And I should see an error Fill in some content before saving 
        And The error should disappear

    Scenario: Submit form then view index
        Given the following sections:
            | name      | content       | 
            | no1       | textify       | 
            | no2       | woot          | 
        And I am on the edit section page for no2
        And I have entered "An edit" in #wmd-input
        When I click on #saveButton
        And I view the main page
        Then I should see the following sections:
            | name      | content       | 
            | no1       | textify       | 
            | no2       | An edit       | 
