"""Errors thrown by the Unresyst application."""

class UnresystError(Exception):
    """The base exception for all exceptions.
    
    Defines the message property.
    """
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message
    message = property(_get_message, _set_message)

    
class SymmetryError(UnresystError):
    """An error for handling symmetric relationship errors.
    
    @type message: string
    @ivar message: the reason for the error
    
    @type object1: object
    @ivar object1: the first object in the relationship
    
    @type object2: object
    @ivar object2: the second object in the relationship
    """
    
    def __init__(self, message, object1, object2):
        """The constructor"""

        self.message = message
        """the reason for the error"""
               
        self.object1 = object1
        """the first object in the relationship"""
        
        self.object2 = object2               
        """the second object in the relationship"""
        
    def __str__(self):
        return ("There's an error in relationship symmetry.\n" + \
               "    message: %s\n" + \
               "    first object in relationship: %s\n" + \
               "    second object in relationship: %s") \
               % (self.message, self.object1, self.object2)    
