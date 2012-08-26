Then /I should see the following rendered sections/ do |table|
  # Give the page time to load
  sleep 0.5
  pageSections = page.all( 'div.listItem' )
  pageSections.length.should == table.hashes.length
  table.hashes.zip pageSections do |expected, actual|
    actual['id'].should == 'section-' + expected['name']
    actual.should have_content(expected['content'])
  end
end
