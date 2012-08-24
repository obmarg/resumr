Given /^I am not logged in$/ do
  Net::HTTP::get( '127.0.0.1', '/systemtest/logout', 43001 )
end

Then /^I should be on the login page$/ do
  current_path_info().should == '/login'
end

Then /^I should see buttons to login using:$/ do |table|
  table.hashes.each do |hash|
    service = hash[ 'service' ]
    page.should have_selector( 
                              "a.zocial.#{service}", 
                              :text => "Sign in with #{service.capitalize}"
                             )
  end
end
