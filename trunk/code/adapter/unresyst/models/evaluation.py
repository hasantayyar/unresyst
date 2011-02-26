"""Models related to recommender evaluation"""

from django.db import models

class BaseEvaluationPair(models.Model):
    """An abstract base class for a test set pair. To be used for
    testing the correctness of the predicted expectancy.
    
    The subclass has to have attributes:
     - subj - a foreign key to subject
     - obj - a foreign key to object    
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
        
        return u"%s - %s: exp: %f, got: %f" % \
            (self.subj, self.obj, self.expected_expectancy, self.obtained_expectancy)
    
    @classmethod
    def export(cls, f):
        """Export evaluation pairs to a csv file of the given name.
        
        @type f: file
        @param f: open file to write to        
        """                
        i = 0
        f.write("# userId, itemId\n")
        
        # loop through the pairs, 
        for subj_id, obj_id in cls.values_list('subj__pk', 'obj__pk'):
                        
            # create the line
            linestr = "%s,%s\n" % (subj_id, obj_id)                        
            
            # write it to the file
            f.write(linestr)
            
            i += 1
        
        print "    %d evaluation pairs exported" % i
            
    # to be implemented by subclasses
    #            
    
    @classmethod
    def select(cls, i=0):
        """Select the pairs for a validation, save them to the database and
        remove them from the system data. The method is called in every 
        iteration.
        
        To be implemented by the subclass.

        @type i: int
        @param i: the number of iteration of the validation (useful when
            cross-validation is done)
        """
        raise NotImplementedError() 

    def get_prediction_success(self):
        """Count whether the pair was successful. The obtained expectancy has
        to be filled first.
        
        To be implemented by the subclass.
        """        
        raise NotImplementedError()
    
