"""The main class of the abstractor package - Abstractor"""

from base import BaseAbstractor
from unresyst.models.common import SubjectObject, Recommender as RecommenderModel
from unresyst.constants import *

class BasicAbstractor(BaseAbstractor):
    """The basic implementation of the Abstractor class"""

    @classmethod
    def create_subjectobjects(cls, recommender_model, subjects, objects):
        """See the base class for documentation."""
        
        # if subjects are the same as objects, use the "so" entity type 
        so = ENTITY_TYPE_SUBJECTOBJECT if subjects == objects else ""

        # create them again. subjects:
        for subj in subjects.iterator():
            
            # create the subject
            subob = SubjectObject(
                id_in_specific=subj.pk,
                name=subj.__unicode__(),
                entity_type=so or ENTITY_TYPE_SUBJECT,
                recommender=recommender_model
            )
            
            # save it
            subob.save()
        
        print "    %d subjects created" % subjects.count()
            
        # for recommenders where subjects==objects, that's it
        if so:
            return
            
        # create objects:                        
        for obj in objects.iterator():
            
            # create the object
            subob = SubjectObject(
                id_in_specific=obj.pk,
                name=obj.__unicode__(),
                entity_type=ENTITY_TYPE_OBJECT,
                recommender=recommender_model
            )
            
            # save it
            subob.save()
            
        print "    %d objects created" % objects.count()


    # tyhle tri se budou asi delat jednotne - jedna metoda, kterou zavolaj  
    # promenne: 
    # trida, ktera se ma vytvaret
    # typy ktere do toho budou vstupovat
    
    @classmethod            
    def create_predicted_relationship_instances(cls, predicted_relationship):
        """See the base class for documentation."""        
        
        # evaluate the relationship for all possible subjectobjects
        predicted_relationship.evaluate()
       
    
    @classmethod        
    def create_relationship_instances(cls, relationships):
        """See the base class for documentation."""

        # evaluate all relationships
        for rel in relationships:
            rel.evaluate()

    
    @classmethod
    def create_rule_instances(cls, rules):
        """See the base class for documentation."""
        
        # eveluate all rules
        for rule in rules:
            rule.evaluate()
