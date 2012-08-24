Given /^I am on the main page$/ do
  visit( '/' )
end

When /I view the main page/ do
  visit( '/' )
end

Given /^I am on the stylesheet page$/ do
  pending # express the regexp above with the code you wish you had
end

Then /^I should be on the stylesheet page$/ do
  pending # express the regexp above with the code you wish you had
end

Then /^I should be on the view section history page for (\w+)$/ do |sectionName|
  current_path_info().should == "/#section/#{sectionName}/history"
end

Then /^I should be on the main page$/ do
  current_path_info().should =~ /\/#?/
end

Given /^I'm on the section history page for (\w+)$/ do |sectionName|
  visit( "/#/section/#{sectionName}/history" )
end

When /^I view the section history page for (\w+)$/ do |sectionName|
  visit( "/#/section/#{sectionName}/history" )
end

Given /^I am on the new section page$/ do
  visit( '/#newSection' )
end

Given /^I am on the edit section page for (\w+)$/ do |sectionName|
  visit( "/#section/#{sectionName}/edit" )
end

Then /^I should be on the new section page$/ do
  current_path_info().should == "/#newSection"
end

Then /^I should be on the edit section page for (\w+)$/ do |sectionName|
  current_path_info().should == "/#section/#{sectionName}/edit"
end


