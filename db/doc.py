
import os
import pygit2
from pygit2 import Repository, init_repository
from gitutils import CommitBlob
from .section import Section
from .constants import MASTER_REF, SECTION_REF_PREFIX

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
        '''
        targetDir = os.path.join( rootPath, name + '.git' )
        if create:
            # Create a bare repository
            self.repo = init_repository( targetDir, True )
            self._CreateMasterBranch()
        else:
            self.repo = Repository( targetDir )

    def _CreateMasterBranch( self ):
        '''
        Creates the master branch on the repo w/ default file.
        For now this is just a file named layout
        '''
        commitId = CommitBlob( 
                self.repo, '', 'layout', 'Initial commit' 
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
        Gets an iterator over the sections
        '''
        return ( 
                Section( name, self.repo[ref.oid], self.repo ) 
                for name, ref in self._SectionRefs()
                )
       
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
