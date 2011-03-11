"""The main class of the abstractor package - Abstractor"""

from base import BaseAbstractor
from unresyst.models.common import SubjectObject, Recommender as RecommenderModel
from unresyst.constants import *

class BasicAbstractor(BaseAbstractor):
    """The basic implementation of the Abstractor class"""


    def create_subjectobjects(self, recommender_model, subjects, objects):
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


    
    def create_predicted_relationship_instances(self, predicted_relationship):
        """See the base class for documentation."""        
        
        # evaluate the relationship for all possible subjectobjects
        predicted_relationship.evaluate()
       
    
    def create_relationship_instances(self, relationships):
        """See the base class for documentation."""

        # evaluate all relationships
        for rel in relationships:
            rel.evaluate()

    
    def create_rule_instances(self, rules):
        """See the base class for documentation."""
        
        # eveluate all rules
        for rule in rules:
            rule.evaluate()

    def create_clusters(self, cluster_sets):
        """See the base class for documentation."""
        
        # evaluate all cluster sets
        for cluster_set in cluster_sets:
            cluster_set.evaluate()          
            
    def create_biases(self, biases):
        """See the base class for documentation."""                      
        
        # evaluate the biases
        for bias in biases:
            bias.evaluate()
            
            
