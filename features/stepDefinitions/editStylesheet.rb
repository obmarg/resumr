Given /I enter "(.*?)" in the stylesheet editor/ do |text|
  # Bit of javascript trickery to set stylesheet editor text.
  # The textbox is hidden, so we're not allowed to edit it the
  # normal way
  page.execute_script "$('#stylesheetEditor').val('#{text}').change()"
end

Then /^the style tag should contain "(.*?)"$/ do |style|
  sleep 0.5
  newpage = Nokogiri::HTML.parse(page.source)
  newpage.css('style').first.text.should include(style)
end
