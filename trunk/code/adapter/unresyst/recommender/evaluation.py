"""The classes related to recommender evaluation"""
import os.path
import codecs

from unresyst.exceptions import EmptyTestSetError
from unresyst.constants import *

from settings import LOG_DIRECTORY

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
    def _get_cleared_pairs(cls):
        """Get the test pairs, check whether they aren't empty and
        clear the results.
        
        @rtype: QuerySet
        @return: the test pairs
        
        @raise EmptyTestSetError: if the set is empty
        """
        # get the dataset and test if not empty
        qs_pairs = cls.EvaluationPairModel.objects.all() 
        
        # remove all previous success and obtained expectancies
        qs_pairs.update(obtained_expectancy=None, is_successful=None)            
        
        if not qs_pairs:
            raise EmptyTestSetError("Call the select_validation_pairs()"+ \
                " method first")     
        
        return qs_pairs

    @staticmethod
    def _open_logfile(directory, filename):
        """Open a log file
        
        @rtype: file
        """
        if directory and filename:
            full_name = os.path.join(directory, filename)
            return codecs.open(full_name, mode='w', encoding='utf-8')

        return None 

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

        @raise EmptyTestSetError: if the test set is empty            
        """
        # if the settings are given, open a log file and log
        fpreds = cls._open_logfile(LOG_DIRECTORY, LOG_PREDICTIONS_FILENAME)
        fhits = cls._open_logfile(LOG_DIRECTORY, LOG_HITS_FILENAME)
            
        # get the pairs
        qs_pairs = cls._get_cleared_pairs()
        all_count = qs_pairs.count()   

        # initialize        
        i = 0
        succ_count = 0
        non_triv_count = 0
        
        print "Processing %d pairs..." % all_count
        
        # go through the pairs
        for pair in qs_pairs.iterator():
            
            # evaluate
            prediction = recommender.predict_relationship(pair.subj, pair.obj)
            
            # log
            if fpreds:
                fpreds.write(u"%s\n" % prediction.__unicode__())
            
            pair.obtained_expectancy = prediction.expectancy
            pair.is_successful = pair.get_success()
            pair.save()                            
            
            i += 1
            
            if i % 100 == 0:
                print "%d pairs processed" % i
                
            if pair.is_successful:
                succ_count += 1
                
                if fhits:
                    fhits.write(u'%s\n' % prediction.__unicode__())
                
                if pair.obtained_expectancy < TRIVIAL_EXPECTANCY:
                    non_triv_count += 1
        
        # this isn't very best practice-following but we don't care for file corruption
        if fhits:
            fhits.close()
            
        if fpreds:
            fpreds.close()
        
        # count and print the success rate        
        cls.success_rate = float(succ_count)/ all_count

        print "Success rate: %f (%d/%d)" % (cls.success_rate, succ_count, all_count)
        print "%d of %d successful predictions were non-trivial." % (non_triv_count, succ_count)
        
        # count the metric        
        return cls.prediction_metric()
    
    @classmethod
    def evaluate_recommendations(cls, recommender, count):
        """Evaluate recommendations obtained for the subjects in the test
        pairs.
        
        @type recommender: Recommender
        @param recommender: the built recommender on which the predictions
            should be evaluated
        
        @type count: int
        @param count: the number of recommendations to get           
            
        @rtype: float
        @return: the result of the metric                    
        """
        # if the settings are given, open a log file and log                                      
        fhits = cls._open_logfile(LOG_DIRECTORY, LOG_HITS_FILENAME)
        frecs = cls._open_logfile(LOG_DIRECTORY, LOG_RECOMMENDATIONS_FILENAME)
        
        # get the cleared pair dataset 
        qs_pairs = cls._get_cleared_pairs()
                
        # take ids of subjects from the test pairs        
        subj_id_list = qs_pairs.values_list('subj__pk',flat=True).distinct()
        
        # take the whole subjects
        qs_subjects = recommender.subjects.filter(pk__in=subj_id_list)        

        i = 0 
        hit_count = 0       
        for subj in qs_subjects:            
        
            i += 1
            
            if i % 10 == 0:
                print "%d subjects processed" % i
                
            # for each subject in the test pair get its recommendations
            recommendations = recommender.get_recommendations(subj, count)            
                
            
            # mark each recommended object that is in the test set as successful
            #
            for rec in recommendations:

                # if it should be logged, log it
                if frecs:
                    frecs.write(u'%s\n' % rec.__unicode__())
                    
                obj = rec.object_
                
                # filter the test pair
                qs_pair = cls.EvaluationPairModel.objects.filter(subj=subj, obj=obj)
                
                # if it's in the test pair mark it as successful
                for pair in qs_pair:
                                    
                    hit_count += 1
                    
                    pair.is_successful = True
                    pair.save()
                    
                    if fhits:
                        fhits.write(u'%s\n' % rec.__unicode__())

        # this isn't very best practice-following but we don't care for file corruption
        if fhits:
            fhits.close()
            
        if frecs:
            frecs.close()
            
        print "%d hits recorded, counting metric..." % hit_count
        
        # count the metric        
        return cls.recommendation_metric(count)
        
    
    

