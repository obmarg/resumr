require 'cucumber/formatter/unicode'
require 'rspec/expectations'
require 'capybara/cucumber'
require 'capybara/poltergeist'
require 'net/http'
require 'json'


Before do
    Capybara.run_server = false
    #Capybara.current_driver = :poltergeist
    Capybara.current_driver = :selenium
    Capybara.app_host = 'http://127.0.0.1:43001'
    Capybara.default_wait_time = 5
end

After do
    Net::HTTP::get( '127.0.0.1', '/systemtest/reset', 43001 )
end
