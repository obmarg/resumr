
import os
from pygit2 import Repository, init_repository
from gitutils import CommitBlob
from .section import Section
from .sectionindex import SectionIndex
from .constants import MASTER_REF, SECTION_REF_PREFIX
from .constants import SECTION_INDEX_FILENAME
from .errors import SectionNotFound, RepoNotFound

rootPath = 'data'


class Document(object):
    '''
    Class representing a document, interacts with the git
    database
    '''

    def __init__( self, name, create=False ):
        '''
        Constructor

        Args:
            name:   The name of the document
            create: If true, will create a document
        Exceptions:
            RepoNotFound if repository isn't found
        '''
        targetDir = os.path.join( rootPath, name + '.git' )
        if create:
            # Create a bare repository
            self.repo = init_repository( targetDir, True )
            self._CreateMasterBranch()
        else:
            try:
                self.repo = Repository( targetDir )
            except KeyError:
                raise RepoNotFound()

    def _CreateMasterBranch( self ):
        '''
        Creates the master branch on the repo w/ default file.
        For now this is just a file named layout
        '''
        commitId = CommitBlob(
                self.repo, '', SECTION_INDEX_FILENAME, 'Initial commit'
                )
        self.repo.create_reference( MASTER_REF, commitId )

    @staticmethod
    def _IsSectionRef( refName ):
        '''
        Checks if a refererence name refers to a section

        Args:
            refName:    The reference name
        Returns:
            A boolean
        '''
        return refName.startswith( SECTION_REF_PREFIX )

    @staticmethod
    def _RefNameToSectionName( refName ):
        '''
        Converts a reference name to a section name

        Args:
            ref:    The reference name
        '''
        return refName[ len(SECTION_REF_PREFIX) : ]

    def _SectionRefs( self ):
        '''
        Gets an iterator over the section refs
        '''
        return (
                (
                    self._RefNameToSectionName( ref ),
                    self.repo.lookup_reference( ref ),
                    )
                for ref in self.repo.listall_references()
                if self._IsSectionRef( ref )
                )

    def Sections( self ):
        '''
        Gets an iterator over all the sections
        '''
        return (
                Section( name, self.repo[ref.oid], self.repo )
                for name, ref in self._SectionRefs()
                )

    def CurrentSections( self ):
        '''
        Gets the current sections with their positions

        Returns:
            A list of tuples ( position, section )
        '''
        return enumerate( self._CurrentSections() )

    def _CurrentSections( self ):
        '''
        Internal method to get the current sections
        in order, without position numbers

        Returns:
            An iterator over the sections
        '''
        index = SectionIndex(self.repo)
        for s in index.CurrentSections():
            yield self.FindSection(s.name)

    def FindSection( self, name ):
        '''
        Finds a section by name

        Args:
            name    The name of the section to find
        Returns:
            The section if found
        Exceptions:
            SectionNotFound if section not found
        '''
        try:
            ref = self.repo.lookup_reference(
                    SECTION_REF_PREFIX + name
                    )
        except KeyError:
            raise SectionNotFound()
        return Section( name, self.repo[ref.oid], self.repo )

    def AddSection( self, name, content='' ):
        '''
        Creates a new section

        Args:
            name        The name of the section
            content     The optional initial content of the
                        section

        Returns:
            The new Section object
        '''
        commitId = CommitBlob(
                self.repo,
                content,
                name,
                'Created section ' + name
                )
        ref = self.repo.create_reference(
                SECTION_REF_PREFIX + name,
                commitId
                )
        return Section( name, self.repo[ ref.oid ], self.repo )
