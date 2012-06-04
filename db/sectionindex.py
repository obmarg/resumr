
import re
from collections import namedtuple
from .constants import MASTER_REF
from .errors import MasterNotFound, BrokenMaster, SectionNotFound

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

    def GetSectionPosition( self, sectionName ):
        '''
        Gets the position of a section

        Args:
            sectionName    The name of the section to find
        Returns:
            The position of the section
        Throws:
            SectionNotFound error if section not found in index
        '''
        matchingSections = [
                s[0] for s in enumerate( self.sections )
                if s[1].name == sectionName
                ]
        if matchingSections:
            return matchingSections[ 0 ]
        else:
            raise SectionNotFound()

    def SetSectionPosition( self, sectionName, newPosition ):
        '''
        Sets the position of a section

        Args:
            sectionName     The name of the section to set
            newPosition     The new position to set
        Throws:
            SectionNotFound If section is not found in index
            ValueError      If newPosition is invalid
        '''
        if newPosition < 0:
            raise ValueError
        currentPosition = self.GetSectionPosition( sectionName )
        if currentPosition != newPosition:
            newSections = []
            sectionToMove = self.sections[ currentPosition ]
            # Recreate the array in the new order
            insertIndex = 0
            for s in self.sections:
                # Skip the original entry
                if s is not sectionToMove:
                    if insertIndex == newPosition:
                        newSections.append( sectionToMove )
                        insertIndex += 1
                    newSections.append( s )
                    insertIndex += 1

            if insertIndex <= newPosition:
                # We haven't added the section yet
                newSections.append( sectionToMove )
            self.sections = newSections
