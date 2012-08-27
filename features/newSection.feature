Feature: Add New Section
    In order to create my CV
    As a user
    I want to add a new section

    Scenario: Open new section page
        Given I am on the main page
        When I click on #newSectionLink
        Then I should be on the new section page
        And I should see "" in #nameField
        And I should see "" in #wmd-input
        And I should see an empty preview

    Scenario Outline: Basic text preview
        Given I am on the new section page
        When I enter <text> in #wmd-input
        Then I should see <text> in the preview

        Examples:
            | text              |
            | hello world       |
            | something good    |
            | BRILLIANT!!!!     |

    Scenario: More complex text preview
        Given I am on the new section page
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

    Scenario: Clear form
        Given I am on the new section page
        And I have entered "Hello" in #nameField
        And I have entered "Some content" in #wmd-input
        When I click on #cancelButton
        Then I should see "" in #nameField
        And I should see "" in #wmd-input
        And I should see an empty preview

    Scenario: Submit form
        Given I am on the new section page
        And I have entered "Hello" in #nameField
        And I have entered "Some content" in #wmd-input
        When I click on #saveButton
        Then I should be on the edit section page for Hello
        And I should see the edit section "Hello" title

     Scenario Outline: Validation failures
        Given I am on the new section page
        And I have entered <name> in #nameField
        And I have entered <content> in #wmd-input
        When I click on #saveButton
        Then I should be on the new section page
        And I should see an error <warn>
        And The error should disappear

        Examples:
            | name  | content   | warn                                      |
            |       |           | Sections can't be saved without a name    |
            | woo   |           | Fill in some content before saving        |
            |       | something | Sections can't be saved without a name    |

    Scenario: Submit first section then view index
        Given I am on the new section page
        And I have entered "Hello" in #nameField
        And I have entered "Some content" in #wmd-input
        When I click on #saveButton
        And I view the main page
        Then I should see the following sections:
            | name      | content       |
            | Hello     | Some content  |

    Scenario: Submit third section then view index
        Given the following sections:
            | name      | content       | 
            | no1       | textify       | 
            | no2       | some text     |
        And I am on the new section page
        And I have entered "Hello" in #nameField
        And I have entered "Some content" in #wmd-input
        When I click on #saveButton
        And I view the main page
        Then I should see the following sections:
            | name      | content       |
            | no1       | textify       | 
            | no2       | some text     |
            | Hello     | Some content  |
