
import unittest
import os
import shutil
from ..doc import Document


class SubsystemTests(unittest.TestCase):
    '''
    Tests the whole db subsystem in action, without using mocks
    '''
    TestDatabaseName = 'db.Subsystemtests'

    def setUp(self):
        pass

    def tearDown(self):
        shutil.rmtree( os.path.join( 'data',
                self.TestDatabaseName + '.git'
                ) )
        try:
            # If empty, remove the data dir
            os.unlink( 'data' )
        except:
            pass

    def testCreate(self):
        # Create a document
        doc = Document(
                self.TestDatabaseName, create=True
                )

        # Create a couple of sections
        s1 = doc.AddSection( 'section1', 'Some content' )
        s2 = doc.AddSection( 'section2', 'Some other content' )

        # Change the content
        s1.SetContent( 'Changed' )
        s2.SetContent( 'Switched' )

        # Verify the contents
        self.assertEqual( 'Changed', s1.CurrentContent() )
        self.assertEqual( 'Switched', s2.CurrentContent() )

        # Verify the positions are as expected
        self.assertEqual( s1.GetPosition(), 0 )
        self.assertEqual( s2.GetPosition(), 1 )

        # Move 1 to 2, and check
        s2.SetPosition( 0 )
        self.assertEqual( s1.GetPosition(), 1 )
        self.assertEqual( s2.GetPosition(), 0 )

        # Now lets re-load the document
        doc = Document( self.TestDatabaseName )
        self.assertEqual( len( list( doc.CurrentSections() ) ), 2 )
        s1 = doc.FindSection( 'section1' )
        s2 = doc.FindSection( 'section2' )

        # Verify positions again
        self.assertEqual( s1.GetPosition(), 1 )
        self.assertEqual( s2.GetPosition(), 0 )

        # Verify section 1s content history
        self.assertEqual(
                list( s1.ContentHistory() ),
                [ 'Changed', 'Some content' ]
                )

        # Remove section 2, reload and check
        doc.RemoveSection( 'section2' )

        doc = Document( self.TestDatabaseName )
        sections = list( doc.CurrentSections() )
        self.assertEqual( len( sections ), 1 )
        self.assertEqual( sections[ 0 ][ 1 ].name, 'section1' )
