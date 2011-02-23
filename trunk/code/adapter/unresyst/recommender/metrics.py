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
