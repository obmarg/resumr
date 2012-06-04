
import re
from collections import namedtuple
from .constants import MASTER_REF
from .errors import MasterNotFound, BrokenMaster

SectionIndexEntry = namedtuple('SectionIndexEntry', ['name'])


class SectionIndex(object):
    '''
    Class that handles the section index
    '''

    # Regular expression for processing lines
    # Currently these are just the name of the section
    _lineRegExp = re.compile('(?P<name>.*)')

    def __init__(self, repo):
        '''
        Loads the section index from the repository

        Params:
            repo - The repository to load from

        Raises:
            MasterNotFound  If master branch not found
            BrokenMaster    If master data couldn't be read
        '''
        pass

    def CurrentSections(self):
        '''
        Returns list of the current sections
        '''
        return self.sections
