"""The main class of the abstractor package - Abstractor"""

from base import BaseAbstractor
from unresyst.models.common import SubjectObject, Recommender as RecommenderModel
from unresyst.constants import *

class BasicAbstractor(BaseAbstractor):
    """The basic implementation of the Abstractor class"""

    @classmethod
    def create_subjectobjects(cls, recommender, subjects, objects):
        """See the base class for documentation."""

        # delete all subjects and objects for the recommender
        # and everything pointing at it.
        SubjectObject.objects.filter(recommender=recommender).delete()
        
        # if subjects are the same as objects, use the "so" entity type 
        so = ENTITY_TYPE_SUBJECTOBJECT if subjects == objects else ""

        # create them again. subjects:
        for subj in subjects.iterator():
            
            # create the subject
            subob = SubjectObject(
                id_in_specific=subj.id,
                name=subj.__unicode__(),
                entity_type=so or ENTITY_TYPE_SUBJECT,
                recommender=recommender
            )
            
            # save it
            subob.save()
            
        # for recommenders where subjects==objects, that's it
        if so:
            return
            
        # create objects:                        
        for obj in objects.iterator():
            
            # create the object
            subob = SubjectObject(
                id_in_specific=obj.id,
                name=obj.__unicode__(),
                entity_type=ENTITY_TYPE_OBJECT,
                recommender=recommender
            )
            
            # save it
            subob.save()


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
    def create_relationship_instances(cls, recommender, relationships):
        """See the base class for documentation."""
        return         
        # evaluate all relationships
        for rel in relationships:
            rel.evaluate(recommender)
    
    @classmethod
    def create_rule_instances(cls, recommender, rules):
        """See the base class for documentation."""
        return
        # eveluate all rules
        for rule in rules:
            rule.evaluate(recommender_model)
