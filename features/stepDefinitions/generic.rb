Given /^I have entered "?(.*?)"? in (#.*?)$/ do |text, field|
  find( field ).set( text )
end

When /^I enter "?(.*?)"? in (#.*?)$/ do |text, field|
  find( field ).set( text )
end

When /^I type into (.*?):$/ do |field, text|
  find( field ).set( text )
end

When /^I click on (.*?)$/ do |element|
  find( element ).click
end

Then /^I should see "?(.*?)"? in ([#\.][-_\w]*?)$/ do |text, field|
  find( field ).should have_content(text)
end

Then /^I should see an (\w+) element containing "(.*?)"$/ do |elementType, text|
  page.should have_selector( elementType, :text => text )
end

Then /^the style tag should contain "(.*?)"$/ do |style|
  sleep 0.5
  newpage = Nokogiri::HTML.parse(page.source)
  newpage.css("style").first.text.should include(style)
end
