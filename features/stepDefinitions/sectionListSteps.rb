Given /^I have no sections$/ do
    # Nothing to do here
end

Given /^the following sections:$/ do |table|
    table.hashes.each do |row|
        req = Net::HTTP::Post.new( 
                           '/api/sections', 
                           initheader = {'Content-Type'=>'application/json'}
                          )
        req.body = row.to_json
        Net::HTTP.new( '127.0.0.1', 43001 ).start { |http| http.request(req) }
    end
end

Given /^I am on the main page$/ do
    visit( '/' )
end

When /I view the main page/ do
    visit( '/' )
end

Then /I should see no sections/ do
    page.should have_no_selector( 'div.section' )
end

Then /I should see the following sections/ do |table|
    # Wait to give the page time to load 
    # (manual indicates this isn't needed, but seems it is...)
    sleep 2
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

Then /^I should be on the edit section page for (\w+)$/ do |sectionName|
    current_path_info().should == "/#section/#{sectionName}/edit"
end

When /^I click the view section history button for (\w+)$/ do |sectionName|
    find( "div#section-#{sectionName} .icon-list" ).click
end

Then /^I should be on the view section history page for (\w+)$/ do |sectionName|
    current_path_info().should == "/#section/#{sectionName}/history"
end
