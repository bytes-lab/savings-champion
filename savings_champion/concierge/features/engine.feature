# Created by josh at 20/11/14
Feature: Simple Portfolio
  In order to help our clients we need to be able to
  take a clients details and produce them a portfolio
  that fits their needs.

  Scenario: Default User with £100k
      Given a typical user
      And this user wants to tie up their money for
        | amount | term |
        | 100000 | 12   |
        | 300000 | 36   |
        | 3000   | 0    |
      And the products available are
        | provider | product | rate | type | fscs_licence | fscs_licence_limit | provider_maximum | maximum | minimum | sc_code |
        | Santander | 123 Current Account | 0.03 | High Interest Current Account | Own Licence | 85000 | 0 | 20000 | 3000 | SC0001 |
        | Santander | 123 Current Account | 0.02 | High Interest Current Account | Own Licence | 85000 | 0 | 1000 | 2000 | SC0002 |
        | Santander | 123 Current Account | 0.01 | High Interest Current Account | Own Licence | 85000 | 0 | 0 | 1000 | SC0003 |
      When the engine is run on the default user
      Then the engine should give recommendations

