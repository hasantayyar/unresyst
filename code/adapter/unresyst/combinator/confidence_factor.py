"""Combinator using confidence factor calculus."""

from base import BaseCombinator


    

class ConfidenceFactorCombinator(BaseCombinator):
    """A combinator using weighted average
    """
    
    def _combine(self, combination_elements, ResultClass):
        """See the base class for documentation"""
        
        res_exp = combination_elements[0].get_expectancy()
        
        # go through the combination elements
        for ce in combination_elements[1:]:
            
            # convert to confidence factors
            res_cf = 2 * res_exp - 1
            ce_cf = 2 * ce.get_expectancy() -1
            
            # count the confidence factor combination
            if res_cf > 0 and ce_cf > 0:            
                comb_cf = res_cf + ce_cf * (1 - res_cf)
                
            elif res_cf < 0 and ce_cf < 0:
                comb_cf = res_cf + ce_cf * (1 + res_cf)
                
            else:
                comb_cf = (res_cf * ce_cf) / (1 - min(abs(res_cf), abs(ce_cf)))
            
            # and back to expectancy
            res_exp = (comb_cf + 1) / 2
        

        desc = self._concat_descriptions(combination_elements)
            
        return ResultClass(expectancy=res_exp, description=desc)
