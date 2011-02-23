"""Models which instances are created by the algorithm package.

The preference between the subject and object in the means of 
the predicted relationship.
"""

from django.db import models

from base import BaseRelationshipInstance

class RelationshipPredictionInstance(BaseRelationshipInstance):
    """The preference between the subject and object in the means of 
    the predicted relationship.
    """
    
    expectancy = models.FloatField()
    """The probability of the predicted relationship appearance between 
    the subject and the object. A number from [0, 1]. 
    """
    
    recommender = models.ForeignKey('unresyst.Recommender')
    """The recommender it belongs to"""
    
    class Meta:
        app_label = 'unresyst'  

    def __unicode__(self):
        return "(%s, %s), %f" % (self.subject_object1, self.subject_object2, self.expectancy)

        
class ExternalPrediction(models.Model):
    """A prediction taken from an external recommender.
    """        
    
    subj_id = models.IntegerField()
    """The id of the subject"""
    
    obj_id = models.IntegerField()
    """The if of the object"""
    
    expectancy = models.FloatField()
    """The probability of the predicted relationship appearance between 
    the subject and the object. A number from [0, 1]. 
    """ 
    
    recommender = models.ForeignKey('unresyst.Recommender')
    """The recommender it belongs to"""  
    
    class Meta:
        app_label = 'unresyst'  
        unique_together = ('subj_id', 'obj_id', 'recommender')

    def __unicode__(self):
        return "(%s, %s), %f" % (self.subj_id, self.obj_id, self.expectancy)      
