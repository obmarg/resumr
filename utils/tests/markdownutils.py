from unittest import TestCase
from ddt import ddt, data
from ..markdownutils import ValidateMarkdown, MarkdownValidationError
from ..markdownutils import CleanMarkdownOutput
import markdown


@ddt
class TestValidateMarkdown(TestCase):

    PassingDataSet = (
            '',
            '#### Something',
            '''
            Hello
            ####
            I am some markdown!  Isn't this great.
            Certainly > than something not great
            ''',
            )

    @data( *PassingDataSet )
    def testPasses(self, data):
        ''' Testing markdown validation passes when expected '''
        ValidateMarkdown(data)

    FailureDataSet = (
            '<a></a>',
            '<b>',
            '<script>',
            '<style>',
            )

    @data( *FailureDataSet )
    def testFailures(self, data):
        ''' Testing markdown validation fails when expected '''
        self.assertRaises(
                MarkdownValidationError,
                lambda: ValidateMarkdown(data)
                )


@ddt
class TestCleanMarkdownOutput(TestCase):
    AllowedTags = (
            'b', 'blockquote', 'code', 'del', 'dd', 'dl', 'dt', 'em', 'h1',
            'h2', 'h3', 'h4', 'h5', 'h6', 'i', 'kbd', 'i', 'kbd', 'li', 'ol',
            'p', 'pre', 's', 'sup', 'sub', 'strong', 'strike', 'ul',
            )
    AllowedStandaloneTags = ('br', 'hr')

    SuccessPairs = [
            '<{0}>somedata</{0}>'.format(tag) for tag in AllowedTags
            ]
    SuccessStandalones = [
            '<{0}/>'.format(tag) for tag in AllowedStandaloneTags
            ] + ['<{0}>'.format(tag) for tag in AllowedStandaloneTags]

    @data(*(SuccessPairs + SuccessStandalones))
    def testWhitelist(self, data):
        '''
        Testing that whitelisted tags are not removed by markdown
        filtering
        '''
        self.assertEqual(data, CleanMarkdownOutput(data))

    MarkdownData = [
            "### A header",
            "#### Another",
            "##### SomeMore",
            '''
            A big header
            ========
            ''',
            '''
            Another
            ----------
            ''',
            '''
            [A titleless link](http://www.somewhere.com)
            [A link with title](www.somewhere.com/a/path "A title")
            ''',
            '*Emphasis*',
            '''
            * An item
            * An item
            ''',
            '''
            # A numbered item
            # A numbered item
            ''',
            '''
                Some code
                Some code
            '''
            ]

    @data(*MarkdownData)
    def testMarkdown(self, data):
        '''
        Testing that processed markdown is not altered by markdown filtering
        '''
        processed = markdown.markdown(data)
        self.assertEqual(processed, CleanMarkdownOutput(processed))

    #TODO: Test image tags

    CleanupTest = [
            ('<script>alert(test)</script>', 'alert(test)'),
            ('<style></style>', ''),
            ('<head>something blah', 'something blah'),
            ]

    @data( *CleanupTest )
    def testCleanup(self, data):
        '''
        Testing that invalid tags are removed by markdown filtering
        '''
        toProcess, expectedResult = data
        self.assertEqual(expectedResult, CleanMarkdownOutput(toProcess))
