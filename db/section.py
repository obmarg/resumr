from gitutils import CommitBlob
from .sectionindex import SectionIndex
from .constants import SECTION_REF_PREFIX


class Section(object):
    '''
    Represents a Section in a document
    '''

    def __init__( self, name, headCommit, repo ):
        '''
        Constructor

        Args:
            name        The name of the section
            headCommit  The head commit of the section
            repo        The repository object
        '''
        self.name = name
        self.headCommit = headCommit
        self.repo = repo

    def CurrentContent( self ):
        '''
        Returns the current content of the section
        '''
        oid = self.headCommit.tree[ 0 ].oid
        blob = self.repo[ oid ]
        return blob.data

    def ContentHistory( self ):
        '''
        Generator function that returns the history of this section

        This niavely assumes there's only one parent commit
        on each commit, which will do for now.
        '''
        current = self.headCommit
        while True:
            oid = current.tree[ 0 ].oid
            yield self.repo[ oid ].data
            if current.parents:
                # current has at least one parent
                current = current.parents[ 0 ]
            else:
                break

    def SetContent( self, newContent ):
        '''
        Adds a new version of the section

        Args:
            newContent  The new content of the section
        '''
        newId = CommitBlob(
                self.repo,
                newContent,
                self.name,
                'Updating section',
                [ self.headCommit ],
                SECTION_REF_PREFIX + self.name
                )
        self.headCommit = self.repo[ newId ]

    def GetPosition( self ):
        '''
        Finds the current position of the section

        Returns:
            The position of this section
        Throws:
            SectionNotFound error if section not found in index
        '''
        index = SectionIndex(self.repo)
        return index.GetSectionPosition( self.name )

    def SetPosition( self, newPosition ):
        '''
        Sets the position of the section

        Args:
            newPosition     The new position of the section
        Throws:
            SectionNotFound error if the section isn't found in the index
        '''
        index = SectionIndex( self.repo )
        index.SetSectionPosition( self.name, newPosition )
