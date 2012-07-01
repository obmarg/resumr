Feature: Login
    In order to keep my data to myself
    As a user
    I want to be able to login

    # Due to the reliance on external services for OAuth, it's
    # somewhat difficult to thoroughly test this.
    # Might mock out the external services in future, but for
    # now I'll just keep the tests *very* simple

    Scenario: Being redirected to login screen
        Given I am not logged in
        When I view the main page
        Then I should be on the login page
        And I should see buttons to login using:
            | service   |
            | facebook  |
            | google    |
