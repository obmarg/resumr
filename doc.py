
import os
import time
import pygit2
from pygit2 import Repository, init_repository

rootPath = 'data'

class Section(object):
    '''
    Represents a Section in a document
    '''

    def __init__( self, name, headCommit ):
        '''
        Constructor
        
        Args:
            name:       The name of the section
            headCommit  The head commit of the section
        '''
        self.name = name
        self.headCommit = headCommit


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
        targetDir = os.path.join( rootPath, name + '.git')
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
                Section( name, self.repo[ref.oid] ) 
                for name, ref in self._SectionRefs()
                )
       
    def AddSection( self, name ):
        '''
        Creates a new section
        
        Returns:
            The new Section object
        '''
        signature = pygit2.Signature(
                'Mr Name',
                'name@domain.com',
                time.time(), 0
                )
        # Need to create an empty blob,
        # Then a tree/commit/both pointing at it
        # Then add a reference repo.create_reference( 'name', oid )
        # Then wrap the reference in a section and return
        blob = self.repo.create_blob( '' )
        builder = self.repo.TreeBuilder()
        builder.insert( name, blob, 0 )
        treeOid = builder.write()
        commitId = self.repo.create_commit(
                None, # Don't update any references just now
                signature,
                signature,
                'Created section ' + name,
                treeOid,
                []
                )
        ref = self.repo.create_reference( 
                self.SECTION_REF_PREFIX + name, 
                commitId 
                )
        return Section( name, self.repo[ ref.oid ] )
