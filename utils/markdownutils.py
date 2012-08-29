import re

all = [
    'CleanMarkdownOutput',
    'ValidateMarkdown',
    'MarkdownValidationError',
    ]

HTML_TAG_REGEXP = re.compile(r'<[^>]*>?')

# (tags that can be opened/closed) | (tags that stand alone)
TAG_WHITELIST = re.compile(
        r'^(<\/?(b|blockquote|code|del|dd|dl|dt|em|h1|h2|h3|h4|h5|h6|i|kbd|'
        r'li|ol|p|pre|s|sup|sub|strong|strike|ul)>|<(br|hr)\s?\/?>)$',
        re.IGNORECASE
        )

# <a href="url..." optional title>|</a>
LINK_WHITELIST = re.compile(
        r'^(<a\shref="((https?|ftp):\/\/|\/)'
        r'[-A-Za-z0-9+&@#\/%?=~_|!:,.;\(\)]'
        r'+"(\stitle="[^"<>]+")?\s?>|<\/a>)$',
        re.IGNORECASE
        )

# <img src="url..." optional width  optional height  optional alt
# optional title >
IMG_WHITELIST = re.compile(
        r'^(<img\ssrc="(https?:\/\/|\/)'
        r'[-A-Za-z0-9+&@#\/%?=~_|!:,.;\(\)]+'
        r'"(\swidth="\d{1,3}")?(\sheight="\d{1,3}")?'
        r'(\salt="[^"<>]*")?(\stitle="[^"<>]*")?\s?\/?>)$',
        re.IGNORECASE
        )

WHITELISTS = (TAG_WHITELIST, LINK_WHITELIST, IMG_WHITELIST)


class MarkdownValidationError(Exception):
    '''
    Validation Error used by Markdown
    '''
    pass


def CleanMarkdownOutput(html):
    '''
    Cleans out all non-valid HTML tags from some already processed markdown
    output

    Generally, this shouldn't be a big deal as MD with invalid characters
    should have been ditched already.  Better safe than sorry though.

    Params:
        html - The html to clean
    Returns:
        Some html with all invalid tags removed
    '''
    def SubFunction(match):
        # The function that handles substitution
        tag = match.group()
        for wl in WHITELISTS:
            if wl.match(tag):
                return tag
        return ""
    # TODO: Could balance tags as well, but let's leave that for now
    return HTML_TAG_REGEXP.sub(SubFunction, html)


def ValidateMarkdown(md):
    '''
    Validates some markdown that's arrived from a user.
    For now, I'm just going to say it should have *no* HTML in it.
    Can change that as images/whatever are needed

    Params:
        md - The markdown to validate
    Throws:
        MarkdownValidationError on failure
    '''
    if HTML_TAG_REGEXP.search(md):
        raise MarkdownValidationError
