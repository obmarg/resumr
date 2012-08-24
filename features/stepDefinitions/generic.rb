Given /^I have entered "?(.*?)"? in (.*?)$/ do |text, field|
  find( field ).set( text )
end

When /^I enter "?(.*?)"? in (.*?)$/ do |text, field|
  find( field ).set( text )
end

When /^I type into (.*?):$/ do |field, text|
  find( field ).set( text )
end

When /^I click on (.*?)$/ do |element|
  find( element ).click
end

Then /^I should see "?(.*?)"? in ([-#\._\w]*?)$/ do |text, field|
  find( field ).should have_content(text)
end

Then /^I should see an (\w+) element containing "(.*?)"$/ do |elementType, text|
  page.should have_selector( elementType, :text => text )
end
