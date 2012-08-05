define([
  'order!static/js/libs/Pagedown/Markdown.Converter.js',
  'order!static/js/libs/Pagedown/Markdown.Sanitizer.js',
  'order!static/js/libs/Pagedown/Markdown.Editor.js',
], function(){
  md = Markdown;
  Markdown = undefined;
  return md;
});
