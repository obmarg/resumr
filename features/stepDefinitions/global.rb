Given /^I have no sections$/ do
  # Nothing to do here
end

def SendData(url, json, method)
  req = method.new(
    url, initheader = {'Content-Type'=>'application/json'}
  )
  req.body = json
  Net::HTTP.new( '127.0.0.1', 43001 ).start { |http| http.request(req) }
end

def DoPost(url, json)
  SendData(url, json, Net::HTTP::Post)
end

def DoPut(url, json)
  SendData(url, json, Net::HTTP::Put)
end

Given /^the following sections:$/ do |table|
  table.hashes.each do |row|
    DoPost('/api/sections', row.to_json)
  end
end

Given /^I have a stylesheet containing "(.*?)"$/ do |style|
  DoPut('/api/stylesheet', {'content'=>style}.to_json)
end

