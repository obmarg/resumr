
import os
from pygit2 import Repository, init_repository
from gitutils import CommitBlob
from .section import Section
from .stylesheet import Stylesheet
from .sectionindex import SectionIndex
from .constants import MASTER_REF, SECTION_REF_PREFIX
from .constants import SECTION_INDEX_FILENAME, STYLESHEET_REF_PREFIX
from .errors import ContentNotFound, RepoNotFound

DEFAULT_ROOT_PATH = 'data'


class Document(object):
    '''
    Class representing a document, interacts with the git
    database
    '''

    def __init__( self, name, create=False, rootPath=None ):
        '''
        Constructor

        Args:
            name        The name of the document
            create      If true, will create a document
            rootPath    The rootPath to use (if not supplied, uses default)
        Exceptions:
            RepoNotFound if repository isn't found
        '''
        if not rootPath:
            rootPath = DEFAULT_ROOT_PATH
        targetDir = os.path.join( rootPath, name + '.git' )
        if create:
            # Create a bare repository
            self.repo = init_repository( targetDir, True )
            self._CreateMasterBranch()
            self._CreateStylesheet()
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

    def _CreateStylesheet( self ):
        # TODO: Create the stylesheet (probably via the stylesheet class)
        pass

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
        return ( self._RefNameToSectionName( ref )
                for ref in self.repo.listall_references()
                if self._IsSectionRef( ref ) )

    def Sections( self ):
        '''
        Gets an iterator over all the sections
        '''
        return (
                Section( name, self.repo )
                for name in self._SectionRefs()
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
        '''
        return Section( name, self.repo )

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
        # TODO: Should probably make sure no such section exists somewhere
        #       I'm thinking that'd be the job of the section class?
        section = Section(name, self.repo, create=True)
        section.Create(content=content)
        index = SectionIndex(self.repo)
        index.AddSection( name )
        index.Save( self.repo )
        return section

    def RemoveSection( self, name ):
        '''
        Removes a section.
        This function does not actually delete the data associated
        with a section, it just removes it from the index.

        Args:
            name    The name of the section to remove
        '''
        index = SectionIndex( self.repo )
        index.RemoveSection( name )
        index.Save( self.repo )

    def GetStylesheet(self):
        '''
        Gets the stylesheet object for this document

        Returns:
            A stylesheet object
        '''
        return Stylesheet( 'stylesheet', self.repo )
