"""The functions used as metrics for the evaluators"""
import math

@classmethod
def rmse(cls):
    """Count and print the result of the RMSE on the evaluation pair model
    
    @type EvaluationPairModel: a model, BaseEvaluationPair subclass
    @param EvaluationPairModel: a model to evaluate on    
    
    @rtype: float
    @return: the RMSE of the predictions
    """
    
    # get the expected, obtained expectancy pairs
    exp_pairs = cls.EvaluationPairModel.objects.values_list(
        'expected_expectancy', 'obtained_expectancy')    
    
    # count the sum of the squares of the differences
    square_sum = sum([pow(exp_e - obt_e, 2) for exp_e, obt_e in exp_pairs])
    
    # get the rmse
    ret_rmse = math.sqrt(square_sum / len(exp_pairs))
    print "RMSE: %f" % ret_rmse
    
    return ret_rmse

    
@classmethod    
def precision_recall(cls, count):
    """Count and print the Precision/Recall measure. 
    
    Both are counted as per-user average
    
    Hit: an object that is both in the recommendation and in the evaluation set.
    
    Precision: number of hits / recommendation list size (=count)
    If a hit appears for an subject-object that is multiple time present in the
    test set, it's counted only once.
    
    Recall: number of hits / number of objects for the subject in the evaluation test
    If a hit appears for an subject-object that is multiple time present in the
    test set, it's counted multiple times.
    
    @type count: int
    @param count: the number of objects in recommendation lists
    
    @rtype: pair float float
    @return: precision, recall    
    """
    
    # hits are successful pairs
    qs_hit_pairs = cls.EvaluationPairModel.objects.filter(is_successful=True)
    
    # take ids of subjects from the test pairs        
    subj_id_list = cls.EvaluationPairModel.objects.values_list('subj__pk', flat=True).distinct()    
    
    subj_count = len(subj_id_list)
    
    unique_hit_pairs = qs_hit_pairs.values_list('subj__pk', 'obj__pk').distinct()
    
    # count the precision as explained in docstring
    # as count is the same for all users this can be counted at once
    precision = float(len(unique_hit_pairs)) / (subj_count * count)
    print "Precision: %f" % precision
        
    recall_sum = 0
    
    # count the average recall / user
    for subj_id in subj_id_list:
        
        # count the parameters per user        
        user_hit_count = qs_hit_pairs.filter(subj__pk=subj_id).count()
        possible_hit_count = cls.EvaluationPairModel.objects.filter(subj__pk=subj_id).count()
        
        subj_recall = float(user_hit_count) / possible_hit_count

        #print "%d precision: %f" % (subj_id, float(user_hit_count)/count)
        #print "%d recall: %f" % (subj_id, subj_recall)
        
        recall_sum += subj_recall
    
    recall = recall_sum / subj_count    

    print "Recall: %f" % recall
    
    return (precision, recall)
