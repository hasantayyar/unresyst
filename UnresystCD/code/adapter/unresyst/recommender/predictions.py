"""The prediction classes. Instances of the class are returned by 
the recommender.
"""

class RelationshipPrediction(object):
    """The prediction of the predicted_relationship appearing between
    the given subject-object pair.
    
    @type subject: the domain-specific subject
    @ivar subject: the subject 
    
    @type object_: the domain-specific object
    @ivar object_: the object
    
    @type expectancy: float
    @ivar expectancy: the estimated probability of the predict_relationship
        occuring between the subject and the object
        
    @type explanation: str
    @ivar explanation: the explanation for the prediction        
    """
    
    def __init__(self, subject, object_, expectancy, is_uncertain, explanation=''):
        """The initializer"""
        
        self.subject = subject
        """The subject"""
        
        self.object_ = object_
        """The object"""
        
        self.expectancy = expectancy
        """The estimated probability of the predicted_relationship
        occuring between the subject and the object.
        """
        
        self.is_uncertain = is_uncertain
        """Is the prediction made without having any information available?"""
        
        self.explanation = explanation
        """The explanation for the prediction"""

    def __unicode__(self):
        return u"%s <- %s: %f, %s" % (
            self.subject, 
            self.object_, 
            self.expectancy, 
            self.explanation
        )
        
    def __repr__(self):
        return "< %s >" % str(self.__unicode__())
