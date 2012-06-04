
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
        try:
            ref = repo.lookup_reference(
                    MASTER_REF
                    )
        except KeyError:
            raise MasterNotFound()
        try:
            commit = repo[ref]
            indexOid = commit.tree['index'].oid
            data = repo[indexOid].data
        except KeyError:
            return BrokenMaster()
        self.ProcessData( data )

    def ProcessData( self, data ):
        '''
        Process data into the sections list
        '''
        self.sections = []
        for line in data.split('\n'):
            m = self._lineRegExp.match(line)
            if not m:
                raise BrokenMaster()
            entry = SectionIndexEntry(m.group('name'))
            self.sections.append(entry)

    def CurrentSections(self):
        '''
        Returns list of the current sections
        '''
        return self.sections
