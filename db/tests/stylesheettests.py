
from ..stylesheet import Stylesheet
from ..constants import STYLESHEET_REF_PREFIX
from .content import ContentTests


class StylesheetTests(ContentTests):
    '''
    Tests the stylesheet class

    Currently, this class doesn't have it's own unique tests, as it just
    inherits from Content
    '''
    TestClass = Stylesheet
    NameToUse = 'stylesheet'
    CommitRefPrefix = STYLESHEET_REF_PREFIX
