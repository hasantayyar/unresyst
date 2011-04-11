"""Evaluator defining a method for the average prediction rank"""

from unresyst.exceptions import EmptyTestSetError
from unresyst.constants import *
from unresyst.recommender.evaluation import BaseEvaluator

def index(seq, f):
    """Return the index of the first item in seq where f(item) == True."""
    return next((i for i in xrange(len(seq)) if f(seq[i])), None)


class RankEvaluator(BaseEvaluator):
    """The evaluator for counting the average prediction rank"""
    
    SUBJ_IDS = []
    """A list of subjects (domain specific ids) that are to be tested"""
    
    
    @classmethod
    def evaluate_predictions(cls, recommender, save_predictions=False):
        """See the base class for documentation.
        
        Here it counts the rank, without calling any metric.
        """
            
        # get the test pairs
        qs_pairs = cls._get_cleared_pairs()
        
        # evaluate the rank for each subject
        # 

        obj_count = recommender.objects.count()
        rank_sum = 0
        rank_count = 0

        print "Evaluating %d subjects" % len(cls.SUBJ_IDS)  
            
        
        # go through the wished subjects
        for subj, i in zip(recommender.subjects.filter(pk__in=cls.SUBJ_IDS), range(1, len(cls.SUBJ_IDS))):
            
            # if the test set for the subject is emty go ahead
            test_set_subj = qs_pairs.filter(subj=subj)            
            if not test_set_subj:
                continue
            
            # create an array of object predictions for the subject
            #
            neg_array = []
            pos_array = []
            uncertain_count = 0 
            
            for obj in recommender.objects.all():
                
                # get the prediction
                exp_prediction = recommender.predict_relationship(subj, obj)
                
                if exp_prediction is None or exp_prediction.is_uncertain: 
                    uncertain_count += 1
                
                # otherwise add it to the right array
                else:
                    arr = neg_array if exp_prediction.expectancy > UNCERTAIN_PREDICTION_VALUE \
                        else pos_array
                        
                    arr.append((obj, exp_prediction.expectancy))
            
            # sort the array by expectancy
            pos_array.sort(key=lambda el: el[1], reverse=True)  
            neg_array.sort(key=lambda el: el[1], reverse=True)  
            
            pos_count = len(pos_array)
            neg_count = len(neg_array)
            
            # count the rank that will be given to uncertains.
            if uncertain_count:
            
                # the rank of the first uncertain
                rank_first = float(pos_count) / (obj_count -1)
                
                # the rank of the last uncertain
                rank_last = float(pos_count + uncertain_count) / (obj_count - 1)
                
                uncertain_rank = (rank_first + rank_last) / 2
            
            rank_count += test_set_subj.count()
            
            # count the rank for all objects for the subjects in the test set
            for obj in test_set_subj:
                
                # try finding it in positives
                ipos = index(pos_array, lambda el: el[0] == obj)
                if not (ipos is None):
                    rank_sum += float(ipos) / (obj_count - 1)
                    continue
                                    
                # try finding it in negatives
                ineg = index(neg_array, lambda el: el[0] == obj)
                if not (ineg is None):
                    rank_sum += float(pos_count + uncertain_count + ineg) / (obj_count - 1)
                    continue
                    
                # otherwise it's uncertain
                rank_sum += uncertain_rank
                            
            print "%d subjects evaluated. current avg rank: %f, current rank count: %d" % (i, rank_sum/rank_count if rank_count else -1.0, rank_count)
                        

        res = rank_sum / rank_count
        
        print "Average rank: %f" % res
        
        return res
