Feature: Section History
    In order to revert mistakes I've made
    As a user
    I want to view the history of my sections

    Scenario: View history with one entry
        Given the following sections:
            | name      | content       |
            | no1       | textify       |
            | no2       | soon          |
        When I view the section history page for no1
        Then I should see the following history entries:
            | content   |
            | textify   |

    Scenario: View history with several entries
        Given the following sections:
            | name      | content       |
            | no1       | textify       |
            | no2       | soon          |
        And the following history entries for no1:
            | content       |
            | something     |
            | somethingelse |
            | somemore      |
        When I view the section history page for no1
        Then I should see the following history entries:
            | content       |
            | somemore      |
            | somethingelse |
            | something     |
            | textify       |

    Scenario: View history with some markdown
        Given the following sections:
            | name          | content               |
            | no1           | ### Hello             |
        And the following history entries for no1:
            | content       |
            | #### Trello   |
        When I view the section history page for no1
        Then I should see an h3 element containing "Hello"
        And I should see an h4 element containing "Trello"


    Scenario: Select history entry
        Given the following sections:
            | name      | content   |
            | no1       | textify   |
            | no2       | something |
        And the following history entries for no1:
            | content   |
            | pies |
            | something |
        And I'm on the section history page for no1
        When I click the select item button for entry 1
        Then I should be on the main page
        And I should see the following sections:
            | name      | content   |
            | no1       | pies      |
            | no2       | something |

    Scenario: Select history entry then reload main page
        Given the following sections:
            | name      | content   |
            | no1       | textify   |
            | no2       | something |
        And the following history entries for no1:
            | content   |
            | pies |
            | something |
        And I'm on the section history page for no1
        When I click the select item button for entry 2
        And I view the main page
        Then I should be on the main page
        And I should see the following sections:
            | name      | content   |
            | no1       | textify   |
            | no2       | something |
