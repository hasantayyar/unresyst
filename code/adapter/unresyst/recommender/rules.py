"""The classes for representing business rules and relationships"""

class Relationship(object):
    """A class representing a relationship between entities (not necessarily 
    of the same type). Contains the condition that is true between and only 
    between the entities that are in the given relationship.
    """
    
    def __init__(self, condition, description=None):
        """The constructor."""
        
        self.condition = condition
        """A boolean function that represents the condition. If True 
        for the given pair of entities, there's the Relationship between the entities. 
        Should be simple.
        """
        
        self.description = description
        """A string describing the rule. Can contain placeholders for entities."""


class _BaseRule(Relationship):
    """A base class for all rules (abstract)."""
    
    def __init__(self, condition, confidence, weight, description=None):
        """The constructor."""
        
        Relationship.__init__(self, condition, description)
        
        self.confidence = confidence
        """A float function giving values from [0, 1] representing the confidence
        of the rule for the given pair. It's dynamic, depends on the entity pair
        """
        
        self.weight = weight
        """An integer number from 0 to 100 representing the *static* weitht of the rule. 
        It doesn't depend on the entity pair.
        """
        
# confidence by taky mohla vracet string s doplnujicim vysvetlenim,         

class _SimilarityRule(_BaseRule):
    """A base class (abstract) for all rules operating between the same type."""
    pass
    

class ObjectSimilarityRule(_SimilarityRule):
    """A class for representing inter-object similarity."""    
    pass


class SubjectSimilarityRule(_SimilarityRule):
    """A class for representing inter-subject similarity."""
    pass


class SubjectObjectRule(_BaseRule):
    """A class for representing subject-object preference for recommendation"""
    pass    

class Bias(object):
    pass    
