Given /^I am on the main page$/ do
    visit( '/' )
end

When /I view the main page/ do
    visit( '/' )
end

Then /I should see no sections/ do
    sleep 0.5
    page.should have_no_selector( 'div.section' )
end

Then /I should see the following sections/ do |table|
    # Wait to give the page time to load 
    # (manual indicates this isn't needed, but seems it is for calls to all)
    sleep 0.5
    # TODO: Would be good to rewrite this to use cucumber's table diff
    pageSections = page.all( 'div.section' )
    pageSections.length.should == table.hashes.length
    table.hashes.zip pageSections do |expected, actual|
        actual['id'].should == 'section-' + expected[ 'name' ]
        actual.should have_content(expected["content"])
    end
end

When /^I click the edit section button for (\w+)$/ do |sectionName|
    find( "div#section-#{sectionName} .icon-edit" ).click
end

When /^I click the view section history button for (\w+)$/ do |sectionName|
    find( "div#section-#{sectionName} .icon-list" ).click
end

Then /^I should be on the view section history page for (\w+)$/ do |sectionName|
    current_path_info().should == "/#section/#{sectionName}/history"
end

When /^I click the move section (\w+) button for (\w+)$/ do |direction, sectionName|
    find( "div#section-#{sectionName} .icon-chevron-#{direction}").click
end

When /^I click the delete section button for (\w+)$/ do |sectionName|
    find( "div#section-#{sectionName} .icon-remove" ).click
end

Then /^I should be on the main page$/ do
    current_path_info().should =~ /\/#?/
end
