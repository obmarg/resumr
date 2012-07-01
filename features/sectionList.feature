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

