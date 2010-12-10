"""The classes for representing business rules and relationships"""

from unresyst.constants import *

class Relationship(object):
    """A class representing a relationship between entities (not necessarily 
    of the same type). Contains the condition that is true between and only 
    between the entities that are in the given relationship.
    """
    
    def __init__(self, condition, description=None):
        """The constructor."""
        
        self.condition = condition
        """A boolean function that represents the condition. If True 
        for the given pair of entities, there's the Relationship between the 
        entities. 
        Should be simple.
        """
        
        self.description = description
        """A string describing the rule. It can contain placeholders for entities: 
        
         - %(subject)s, %(object)s for subject-object relationships and rules
         - %(subject1)s, %(subject2)s for subject-subject relationships 
            and rules
         - %(object1)s, %(object2)s for object-object relationships and rules
         - %(subjectobject1)s, %(subjectobject2)s for recommenders where 
            subject domain is the same as object domain        
        """
    
    on_left = ENTITY_TYPE_SUBJECT
    """The manager that is on left for condition and expectancy functions"""
    
    on_right = ENTITY_TYPE_OBJECT
    """The manager that is on left for condition and expectancy functions"""    
    
    def create_instances(self):
        """Create and save rule instances.
        """
        
        """
        r (relationship/rule)
        create definition, save
        
        
        
        if <to co ma byt vpravo> == <to co ma byt vlevo>:
            nejak vychytat, aby se to pro kazdy par delalo jen jednou
        else    
        for so1 in <to co ma byt vlevo>:
            for so2 in <to co ma byt vpravo>:
                if r.condition(so1, so2):
                    create instance including expectancy
                    save
        """        
        pass
        


class _WeightedRelationship(Relationship):
    """A class representing a relationship with a weight."""

    def __init__(self, condition, weight, description=None):
        """The constructor."""
        
        super(_WeightedRelationship, self).__init__(condition, description)
        
        self.weight = weight
        """A float number from [0, 1] representing the *static* weight of the rule. 
        It doesn't depend on the entity pair.
        """        
        
        

class SubjectObjectRelationship(_WeightedRelationship):
    """A class for representing subject-object preference for recommendation"""
    pass 

class _SimilarityRelationship(_WeightedRelationship):
    """A base class (abstract) for all relationships operating between the same type 
    and meaning similarity.
    """
    pass
    

class ObjectSimilarityRelationship(_SimilarityRelationship):
    """A class for representing inter-object similarity."""    
    pass


class SubjectSimilarityRelationship(_SimilarityRelationship):
    """A class for representing inter-subject similarity."""
    pass

# rules:
# 

class _BaseRule(_WeightedRelationship):
    """A base class for all rules (abstract)."""
    
    def __init__(self, condition, weight, expectancy, description=None):
        """The constructor."""
        
        super(_BaseRule, self).__init__(condition, weight, description)
        
        self.expectancy = expectancy
        """A float function giving values from [0, 1] representing the confidence
        of the rule for the given pair. It's dynamic, depends on the entity pair.
        """
        
        
# confidence by taky mohla vracet string s doplnujicim vysvetlenim,         

class _SimilarityRule(_BaseRule):
    """A base class (abstract) for all rules operating between the same type 
    and meaning similarity."""
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
