require 'cucumber/formatter/unicode'
require 'rspec/expectations'
require 'capybara/cucumber'
require 'capybara/poltergeist'

Capybara.run_server = false
Capybara.current_driver = :poltergeist
Capybara.app_host = 'http://www.resumr.net'

Before do
    # TODO: Setup remote server?
end

After do
    # TODO: Tear down remote server?
end
