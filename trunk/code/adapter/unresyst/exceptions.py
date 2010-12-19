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

class ConfigurationError(UnresystError):
    """Exception meaning that something is wrong in the recommender configuration.        

    @type message: string
    @ivar message: the reason why the parameter is invalid
    
    @type parameter_name: string
    @ivar parameter_name: the name of the invalid parameter
    
    @type parameter_value: object
    @ivar parameter_value: the current (invalid) parameter value    
    """
    
    def __init__(self, message, parameter_name, parameter_value):
        """The constructor."""        

        self.message = message
        """The message saying why the parameter is invalid""" 
        
        self.parameter_name = parameter_name
        """The name of the invalid parameter"""
        
        self.parameter_value = parameter_value
        """The current (invalid) value of the parameter"""      

    def __str__(self):
        return ("A configuration parameter is invalid.\n" + \
               "    message: %s\n" + \
               "    parameter name: %s\n" + \
               "    parameter value: %s") \
               % (self.message, self.parameter_name, self.parameter_value)


class RuleRelationshipError(UnresystError):
    """An error in the configuration of rules/relationships.

    @type message: str
    @ivar message: additional message
    
    @type name: str
    @ivar name: the name of the rule/relationship where the error occured    
    """
    
    def __init__(self, message, name):
        """The constructor."""        

        self.message = message
        """The message saying what's wrong""" 
        
        self.name = name
        """The rule/relationship name"""
    

class DescriptionKeyError(RuleRelationshipError):
    """Exception meaning that there are wrong strings in the rule/relationship
    description.   

    @type message: str
    @ivar message: additional message
    
    @type name: str
    @ivar name: the name of the rule/relationship where the error occured
    
    @type key: str
    @ivar key: the key that shouldn't have been there
    
    @type permitted_keys: str list
    @ivar permitted_keys: the keys that can be in the description
    """
    
    def __init__(self, message, name, key, permitted_keys):
        """The constructor."""        

        super(DescriptionKeyError, self).__init__(message, name)
        
        self.key = key
        """The string key that is wrong"""
        
        self.permitted_keys = permitted_keys
        """The list of permitted keys"""


    def __str__(self):
        return ("There's an invalid format key '%s' in the rule/relationship description.\n" + \
               "    message: %s\n" + \
               "    rule/relationship name: %s\n" + \
               "    the invalid key: %s\n" + \
               "    The permitted keys are: %s") \
               % (self.key, self.message, self.name, self.key, self.permitted_keys) 
                       
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
