'''
File containing utilities for git repositories
'''

import time
import pygit2

def CommitBlob(
        repo,
        content,
        name,
        commitMessage,
        parentCommits = [],
        updateRef = None
        ):
    '''
    Creates a commit containing a single blob

    Args:
        repo            Repository to act on
        content         The content to commit
        name            The name of the blob
        commitMessage   The message to use for the commit
        parentCommits   Parent commit objects
        updateRef       Reference to update

    Returns:
        oid of the new commit
    '''
    
    # Need to create an empty blob,
    # Then a tree/commit/both pointing at it
    # Then add a reference repo.create_reference( 'name', oid )
    # Then wrap the reference in a section and return

    signature = pygit2.Signature(
            'Mr Name',
            'name@domain.com',
            time.time(), 0
            )

    blob = repo.create_blob( content )
    if parentCommits:
        builder = repo.TreeBuilder( parentCommits[ 0 ].tree )
    else:
        builder = repo.TreeBuilder()
    builder.insert( name, blob, 0 )
    treeOid = builder.write()

    commitId = repo.create_commit(
            updateRef,
            signature,
            signature,
            commitMessage,
            treeOid,
            [ c.oid for c in parentCommits ]
            )
    return commitId
