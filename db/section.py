from .sectionindex import SectionIndex
from .content import Content
from .constants import SECTION_REF_PREFIX


class Section(Content):
    '''
    Represents a Section in a document
    '''
    ContentRefPrefix = SECTION_REF_PREFIX

    def GetPosition( self ):
        '''
        Finds the current position of the section

        Returns:
            The position of this section
        Throws:
            ContentNotFound error if section not found in index
        '''
        index = SectionIndex(self.repo)
        return index.GetSectionPosition( self.name )

    def SetPosition( self, newPosition ):
        '''
        Sets the position of the section

        Args:
            newPosition     The new position of the section
        Throws:
            ContentNotFound error if the section isn't found in the index
        '''
        index = SectionIndex( self.repo )
        index.SetSectionPosition( self.name, newPosition )
        index.Save( self.repo )
