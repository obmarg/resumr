Given /^the following history entries for (\w+):$/ do |sectionName, table|
  table.hashes.each do |row|
    req = Net::HTTP::Put.new( 
        "/api/sections/#{sectionName}", 
        initheader = {'Content-Type'=>'application/json'}
        )
    req.body = row.to_json
    Net::HTTP.new( '127.0.0.1', 43001 ).start { |http| http.request(req) }
  end
end

When /^I click the select item button for entry (\d+)$/ do |entryNum|
  sleep 0.5
  historyItems = page.all( 'div.historyItem' )
  num = Integer( entryNum )
  historyItems[ num ].find( '.icon-ok' ).click
end

Then /^I should see the following history entries:$/ do |table|
  sleep 0.5
  historyItems = page.all( 'div.historyItem' )
  actual = [ [ 'content' ] ]
  historyItems.each do |item|
    actual.push( [ item.text ] )
  end
  table.diff!( actual )
end
