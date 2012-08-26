define(
  [],
  () ->
    class Styler

      cssRegexp: /(\}?)\s*(.*?)\{/gm

      constructor: (@elementId, @parentCssSelector) ->

      localiseCss: (content) ->
        content.replace(@cssRegexp, "$1\n\n#{@parentCssSelector} $2{")

      update: (content) ->
        selector = '#' + @elementId 
        css = $(selector)
        if css.size() == 0
          $( 'head' ).append(
            "<style id='#{@elementId}'></style>"
          )
          css = $(selector)
        elem = css[0]
        css.text(@localiseCss(content))

)
