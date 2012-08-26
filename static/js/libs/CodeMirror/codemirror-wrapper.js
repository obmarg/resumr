define([
  'order!static/js/libs/CodeMirror/codemirror.js',
  'order!static/js/libs/CodeMirror/mode/css.js',
], function(){
  cm = CodeMirror;
  CodeMirror = undefined;
  return cm;
});
