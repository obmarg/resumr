Given /I enter "(.*?)" in the stylesheet editor/ do |text|
  page.execute_script "$('#stylesheetEditor').val('#{text}').change()"
end
