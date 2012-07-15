import gitutils


class Content(object):
    '''
    Base class for data that has current content & history.
    e.g. Sections & Stylesheets

    ContentRefPrefix class variable should be overridden by subclasses
    to provide the prefix to the branch names
    '''
    ContentRefPrefix = None

    def __init__(self, name, headCommit, repo):
        '''
        Constructor

        Args:
            name        The name of the content
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
        newId = gitutils.CommitBlob(
                self.repo,
                newContent,
                self.name,
                'Updating section',
                [ self.headCommit ],
                self.ContentRefPrefix + self.name
                )
        self.headCommit = self.repo[ newId ]

