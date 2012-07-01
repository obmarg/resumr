Then /^I should be on the new section page$/ do
    current_path_info().should == "/#newSection"
end

Then /^I should see an empty preview$/ do
    find( '#wmd-preview' ).should have_content( '' )
end

Given /^I am on the new section page$/ do
    visit( '/#newSection' )
end

Then /^I should see "?(.*?)"? in the preview$/ do |text|
    find( '#wmd-preview' ).should have_content( text )
end

Then /^I should see a list containing:$/ do |table|
    # table is a Cucumber::Ast::Table
    lists = page.all( 'ul' )
    found = false
    lists.each do |list|
        children = list.all( 'li' )
        if children.length == table.hashes.length
            found = true
            children.zip table.hashes do |li, item|
                if li.text != item['item']
                    found = false
                end
            end
        end
    end
    found.should == true
end

Then /^I should see the edit section "(.*?)" title$/ do |sectionName|
    page.should have_selector( "h3", :text => /Editing Section "#{sectionName}"/ )
end

Then /^I should see an error (.*?)$/ do |errorText|
    page.should have_selector( "#editorError.opaque", :text => errorText )
end

Then /^The error should disappear$/ do
    page.should_not have_selector( '#editorError.opaque' )
    page.should have_selector( '#editorError.transparent' )
end
