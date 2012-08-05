
import re
from collections import namedtuple
from .constants import MASTER_REF, SECTION_INDEX_FILENAME
from .errors import MasterNotFound, BrokenMaster, ContentNotFound
from .gitutils import CommitBlob

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
        self.sections = []
        try:
            commit = self._lookupHead( repo )
            indexOid = commit.tree[ SECTION_INDEX_FILENAME ].oid
            data = repo[indexOid].data
        except KeyError:
            raise BrokenMaster()
        self.ProcessData( data )

    @staticmethod
    def _lookupHead( repo ):
        # Returns the head commit object (or excepts)
        try:
            return repo[ repo.lookup_reference( MASTER_REF ).oid ]
        except KeyError:
            raise MasterNotFound

    def ProcessData( self, data ):
        '''
        Process data into the sections list
        '''
        self.sections = []
        if not data:
            return
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

    def AddSection( self, name ):
        '''
        Adds a section.
        New sections always go on the end of the list

        Args:
            name    The name for the new section
        '''
        self.sections.append( SectionIndexEntry( name ) )

    def RemoveSection( self, name ):
        '''
        Removes a section from the index

        Args:
            name    The name of the section to remove
        '''
        toRemove = SectionIndexEntry( name )
        try:
            self.sections.remove( toRemove )
        except ValueError:
            # Can't remove if not there.  But shouldn't be fatal, so don't
            # error
            pass

    def GetSectionPosition( self, sectionName ):
        '''
        Gets the position of a section

        Args:
            sectionName    The name of the section to find
        Returns:
            The position of the section
        Throws:
            ContentNotFound error if section not found in index
        '''
        matchingSections = [
                s[0] for s in enumerate( self.sections )
                if s[1].name == sectionName
                ]
        if matchingSections:
            return matchingSections[ 0 ]
        else:
            raise ContentNotFound()

    def SetSectionPosition( self, sectionName, newPosition ):
        '''
        Sets the position of a section

        Args:
            sectionName     The name of the section to set
            newPosition     The new position to set
        Throws:
            ContentNotFound If section is not found in index
            ValueError      If newPosition is invalid
        '''
        if newPosition < 0:
            raise ValueError
        currentPosition = self.GetSectionPosition( sectionName )
        if currentPosition != newPosition:
            self._DoSetSectionPosition( currentPosition, newPosition )

    def _DoSetSectionPosition( self, currentPosition, newPosition ):
        '''
        Internal section position set function.  Does the position switching,
        and assumes all arguments have already been validated
        '''
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

    def Save( self, repo ):
        '''
        Saves a new revision the section index

        Args:
            repo    The repository to save to
        '''
        data = self.GetIndexString()
        CommitBlob(
                repo,
                data,
                SECTION_INDEX_FILENAME,
                'saving section index',
                [ self._lookupHead( repo ) ],
                MASTER_REF
                )

    def GetIndexString( self ):
        '''
        Gets the section data as a string for saving

        Returns:
            The section data as a string
        '''
        return '\n'.join( [ s.name for s in self.sections ] )
