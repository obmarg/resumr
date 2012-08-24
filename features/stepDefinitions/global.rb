Given /^I have no sections$/ do
  # Nothing to do here
end

Given /^the following sections:$/ do |table|
  table.hashes.each do |row|
    req = Net::HTTP::Post.new(
      '/api/sections', initheader = {'Content-Type'=>'application/json'}
    )
    req.body = row.to_json
    Net::HTTP.new( '127.0.0.1', 43001 ).start { |http| http.request(req) }
  end
end


