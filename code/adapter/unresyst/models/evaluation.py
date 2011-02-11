"""Models related to recommender evaluation"""

from django.db import models

class ValidationPair(models.Model):
    """An abstract base class for a test set pair. To be used for
    testing the correctness of the predicted expectancy.
    
    The subclass has to have attributes:
     - subject - a foreign key to subject
     - object_ - a foreign key to object    
    """    
    
    obtained_expectancy = models.FloatField(null=True)
    """The predicted expectancy obtained by the predict_relationship recommender
    method.
    """
    
    expected_expectancy = models.FloatField()
    """The expected expectancy value for the pair"""
    
    is_successful = models.NullBooleanField(null=True)
    """A sign whether the pair prediction was successful"""
    
    class Meta:
        abstract = True
        app_label = 'unresyst'

    def __unicode__(self):
        """Return a textual representation."""    
        
        return u"%s - %s" % (self.subj, self.obj)
    
    @classmethod
    def select_validation_pairs(cls, i=0):
        """Select the pairs for a validation, save them to the database and
        remove them from the system data. The method is called in every 
        iteration.
        
        To be implemented by the subclass.

        @type i: int
        @param i: the number of iteration of the validation (useful when
            cross-validation is done)
        """
        raise NotImplementedError() 

    def get_success(self):
        """Count whether the pair was successful. The obtained expectancy has
        to be filled first.
        
        To be implemented by the subclass.
        """        
        raise NotImplementedError()
    
