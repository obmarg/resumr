import gitutils
from .errors import ContentNotFound


class Content(object):
    '''
    Base class for data that has current content & history.
    e.g. Sections & Stylesheets

    Class Variables:
        ContentRefPrefix    Should be overridden by subclasses
                            to provide the prefix to the branch names
        AutoCreate          If true, the section will always be created if it
                            does not already exist.
        DefaultContent      The default content that will be used when creating
    '''
    ContentRefPrefix = None
    AutoCreate = False
    DefaultContent = ''

    def __init__(self, name, repo, create=False):
        '''
        Constructor

        Args:
            name        The name of the content
            repo        The repository object
            create      This content will be created if it
                        doesn't already exist
        '''
        self.name = name
        self.repo = repo
        self._create = create or self.AutoCreate
        self._headCommit = None
        self._refName = self.ContentRefPrefix + name

    def _GetHeadCommit( self ):
        '''
        Returns the head commit of this content, creating it if neccesary
        '''
        if not self._headCommit:
            try:
                ref = self.repo.lookup_reference( self._refName )
            except KeyError:
                if not self._create:
                    raise ContentNotFound()
                ref = self.Create()
            self._headCommit = self.repo[ ref.oid ]
        return self._headCommit

    def Create( self, content=None ):
        '''
        Creates an initial commit for this content, and sets up a ref (branch)

        Params:
            content     The content to use for the new section

        Returns:
            The created reference
        '''
        commitId = gitutils.CommitBlob(
                self.repo, content or self.DefaultContent, self.name,
                'Create content "{0}"'.format( self.name )
                )
        return self.repo.create_reference( self._refName, commitId )

    def CurrentContent( self ):
        '''
        Returns the current content
        '''
        oid = self._GetHeadCommit().tree[ 0 ].oid
        blob = self.repo[ oid ]
        return blob.data

    def ContentHistory( self ):
        '''
        Generator function that returns the history of the content

        This niavely assumes there's only one parent commit
        on each commit, which will do for now.
        '''
        current = self._GetHeadCommit()
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
        Adds a new version of the content

        Args:
            newContent  The new content of the content
        '''
        newId = gitutils.CommitBlob(
                self.repo,
                newContent,
                self.name,
                'Updating content',
                [ self._GetHeadCommit() ],
                self._refName
                )
        self._headCommit = self.repo[ newId ]

