
import os
import time
import pygit2
from pygit2 import Repository, init_repository
from gitutils import CommitBlob

rootPath = 'data'

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
                Document.SECTION_REF_PREFIX + self.name
                )
        self.headCommit = self.repo[ newId ]


class Document(object):
    '''
    Class representing a document, interacts with the git 
    database
    '''
    SECTION_REF_PREFIX = 'refs/heads/sections/'

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
        else:
            self.repo = Repository( targetDir )

    @classmethod
    def _IsSectionRef( cls, refName ):
        '''
        Checks if a refererence name refers to a section
        
        Args:
            refName:    The reference name
        Returns:
            A boolean
        '''
        return refName.startswith( cls.SECTION_REF_PREFIX )

    @classmethod
    def _RefNameToSectionName( cls, refName ):
        '''
        Converts a reference name to a section name
        
        Args:
            ref:    The reference name
        '''
        return refName[ len(cls.SECTION_REF_PREFIX) : ]

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
       
    def AddSection( self, name ):
        '''
        Creates a new section
        
        Returns:
            The new Section object
        '''
        commitId = CommitBlob(
                self.repo,
                '',
                name,
                'Created section ' + name
                )
        ref = self.repo.create_reference( 
                self.SECTION_REF_PREFIX + name, 
                commitId 
                )
        return Section( name, self.repo[ ref.oid ], self.repo )
