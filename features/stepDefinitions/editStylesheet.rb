Given /I enter "(.*?)" in the stylesheet editor/ do |text|
  # Bit of javascript trickery to set stylesheet editor text.
  # The textbox is hidden, so we're not allowed to edit it the
  # normal way
  page.execute_script "$('#stylesheetEditor').val('#{text}').change()"
end
