Feature: SectionList
    In order to make my CV better
    As a user
    I want to view my currently enabled sections

    Scenario: No sections
        Given I have no sections
        When I view the main page
        Then I should see no sections

    Scenario: View some sections 
        Given the following sections:
          | name      | content       | 
          | no1       | textify       | 
          | no2       | boom          | 
          | asdasd    | something     | 
          | REALLY    | some text     | 
        When I view the main page
        Then I should see the following sections:
          | name      | content       | 
          | no1       | textify       | 
          | no2       | boom          | 
          | asdasd    | something     | 
          | REALLY    | some text     | 

    Scenario Outline: Click edit section
        Given the following sections:
          | name      | content       | 
          | no1       | textify       | 
          | no2       | boom          | 
        And I am on the main page
        When I click the edit section button for <section>
        Then I should be on the edit section page for <section>

        Examples:
            | section   |
            | no1       |
            | no2       |

    Scenario Outline: Click section history
        Given the following sections:
          | name      | content       | 
          | no1       | textify       | 
          | no2       | boom          | 
        And I am on the main page
        When I click the view section history button for <section>
        Then I should be on the view section history page for <section>

        Examples:
            | section   |
            | no1       |
            | no2       |


    Scenario: Move section up
        Given the following sections:
          | name      | content       | 
          | no1       | textify       | 
          | no2       | boom          | 
          | no3       | shaketheroom  | 
        And I am on the main page
        When I click the move section up button for no2
        Then I should see the following sections:
          | name      | content       | 
          | no2       | boom          | 
          | no1       | textify       | 
          | no3       | shaketheroom  | 

    Scenario: Can't move section up
        Given the following sections:
          | name      | content       | 
          | no1       | textify       | 
          | no2       | boom          | 
          | no3       | shaketheroom  | 
        And I am on the main page
        When I click the move section up button for no1
        Then I should see the following sections:
          | name      | content       | 
          | no1       | textify       | 
          | no2       | boom          | 
          | no3       | shaketheroom  | 

    Scenario: Move section down
        Given the following sections:
          | name      | content       | 
          | no1       | textify       | 
          | no2       | boom          | 
          | no3       | shaketheroom  | 
        And I am on the main page
        When I click the move section down button for no1
        Then I should see the following sections:
          | name      | content       | 
          | no2       | boom          | 
          | no1       | textify       | 
          | no3       | shaketheroom  | 

    Scenario: Can't move section down
        Given the following sections:
          | name      | content       | 
          | no1       | textify       | 
          | no2       | boom          | 
          | no3       | shaketheroom  | 
        And I am on the main page
        When I click the move section down button for no3
        Then I should see the following sections:
          | name      | content       | 
          | no1       | textify       | 
          | no2       | boom          | 
          | no3       | shaketheroom  | 
