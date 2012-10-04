from .base import BaseTest
import flask.ext.should_dsl
from should_dsl import should
from db import Section, Document, Stylesheet
from views import render

# Let's keep pyflakes happy
flask.ext.should_dsl
contain = have_content = be_200 = None


class TestRenderView(BaseTest):

    def setUp(self):
        super( TestRenderView, self ).setUp()
        self.mox.StubOutWithMock(render, 'CleanMarkdownOutput')
        self.mox.StubOutWithMock(render, 'GetDoc' )
        self.mox.StubOutWithMock(render, 'IsLoggedIn')
        self.mox.StubOutWithMock(render.markdown, 'markdown')

    def should_render(self):
        render.IsLoggedIn().AndReturn( True )
        doc = self.mox.CreateMock(Document)
        render.GetDoc().AndReturn(doc)

        sections = [
                (i, self.mox.CreateMock(Section)) for i in range(100)
                ]

        doc.CurrentSections().AndReturn(sections)

        expected = []
        for i, s in sections:
            s.name = '%i' % i
            contentStr = 'content' + str(i)
            s.CurrentContent().AndReturn(contentStr)

        for i, s in sections:
            contentStr = 'content' + str(i)
            markdownStr = 'markdown' + str(i)
            cleanStr = 'clean' + str(i)
            render.markdown.markdown(
                    contentStr
                    ).AndReturn( markdownStr )
            render.CleanMarkdownOutput(
                    markdownStr
                    ).AndReturn(cleanStr)
            expected.append(dict(name='%i' % i, content=cleanStr))

        mockStylesheet = self.mox.CreateMock( Stylesheet )
        doc.GetStylesheet().AndReturn( mockStylesheet )
        mockStylesheet.CurrentContent().AndReturn('h3 {}')

        self.mox.ReplayAll()
        response = self.client.get( '/render' )
        response |should| be_200
        self.assertTemplateUsed( 'render.html' )
        self.assertContext( 'sections', expected )
        self.assertContext( 'stylesheet', 'h3 {}' )

        # Check that the output contains all the expected text
        for text in expected:
            response.data |should| contain(text['content'])
        response.data |should| contain('h3 {}')

    def should_redirect_to_login_if_not_logged_in(self):
        render.IsLoggedIn().AndReturn( False )

        self.mox.ReplayAll()
        rv = self.client.get( '/render' )
        self.mox.VerifyAll()
        self.assertRedirects( rv, '/login' )
