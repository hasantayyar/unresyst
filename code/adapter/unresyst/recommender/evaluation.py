"""The classes related to recommender evaluation"""

from unresyst.exceptions import EmptyTestSetError
from unresyst.constants import *

class BaseEvaluator(object):
    """The base class for all evaluators"""
    
    EvaluationPairModel = None
    """The model of the class containing testing pairs. To be overriden.
    A EvaluationPair subclass.
    """
    
    prediction_metric = None
    """A function taking the test pair model that is called on the evaluated pairs
    to obtain a number 
    """
    
    recommendation_metric = None
    """A function taking the test pair model and number of desired recommendations,
    that is called on the evaluated pair model to obtain a number 
    """
    
    # methods to be called before the build:
    # 
    
    @classmethod
    def select_evaluation_pairs(cls):
        """Select the pairs for recommender evaluation.
        
        The selected pairs will be added to the EvaluationPairModel and
        removed from the models where they are now
        """
        cls.EvaluationPairModel.select()
        
    
    @classmethod
    def export_evaluation_pairs(cls, filename):
        """Export the evaluation pair ids to a csv 
        file of the given name.
        
        @type filename: str
        @param filename: the full path to the file
        
        @raise FileNotExists and other file open errors.
        """
        
        with open(filename, 'w') as f:
                
            # export the relationships to the given file
            cls.EvaluationPairModel.export(f)

    
    # methods to be called after the build:
    # 
            
    @classmethod
    def evaluate_predictions(cls, recommender):
        """Evaluate each evaluation pair by calling the predict_relationship
        method.
        
        The results are written to the pair model
        
        @type recommender: Recommender
        @param recommender: the built recommender on which the predictions
            should be evaluated                   
            
        @rtype: float
        @return: the result of the metric                
        """
        
        # get the dataset and test if not empty
        qs_pairs = cls.EvaluationPairModel.objects.all() 
        
        # remove all previous success and obtained expectancies
        qs_pairs.update(obtained_expectancy=None, is_successful=None)
          
        all_count = qs_pairs.count()     
        
        if not qs_pairs:
            raise EmptyTestSetError("Call the select_validation_pairs()"+ \
                " method first")        
        
        i = 0
        succ_count = 0
        non_triv_count = 0
        
        print "Processing %d pairs..." % all_count
        
        # go through the pairs
        for pair in qs_pairs.iterator():
            
            # evaluate
            pair.obtained_expectancy = recommender.predict_relationship(pair.subj, pair.obj).expectancy           
            pair.is_successful = pair.get_success()
            pair.save()                            
            
            i += 1
            
            if i % 100 == 0:
                print "%d pairs processed" % i
                
            if pair.is_successful:
                succ_count += 1
                
                if pair.obtained_expectancy < TRIVIAL_EXPECTANCY:
                    non_triv_count += 1
            
        
        # count and print the success rate        
        cls.success_rate = float(succ_count)/ all_count

        print "Success rate: %f (%d/%d)" % (cls.success_rate, succ_count, all_count)
        print "%d of %d successful predictions were non-trivial." % (non_triv_count, succ_count)
        
        # count the metric        
        return cls.prediction_metric()

    
    @classmethod
    def evaluate_recommendations(cls, recommender, count, metric):
        """Evaluate recommendations obtained for the subjects in the test
        pairs.
        
        @type recommender: Recommender
        @param recommender: the built recommender on which the predictions
            should be evaluated
        
        @type count: int
        @param count: the number of recommendations to get
        
        @type metric: function taking the test pair model
        @param metric: the function that is called on the evaluated pairs
            to obtain a number    
            
        @rtype: float
        @return: the result of the metric                    
        """
        #TODO: dodelat
        # remove all previous values of obtained expectancy
        
        # order the test pairs by subject

        # for each subject in the test pair get its recommendations
        
        # mark the pairs that are in the recommendation list as successful
        
        # call the metric
        pass
    
    

