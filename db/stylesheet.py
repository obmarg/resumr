from .content import Content
from .constants import STYLESHEET_REF_PREFIX


class Stylesheet(Content):
    '''
    Class that manages the stylesheet for a document
    '''
    ContentRefPrefix = STYLESHEET_REF_PREFIX

    def __init__(self, name, *pargs, **kwargs):
        '''
        Constructor.

        Args:
            name        This parameter is ignored, and only kept for
                        compatability
            pargs       Passed through to parent class
            kwargs      Passed through to parent class
        '''
        super(Stylesheet, self).__init__('stylesheet', *pargs, **kwargs)
