"""Combinator using a weighted average."""

from base import BaseCombinator
from unresyst.exceptions import CombinatorError

class AverageCombinator(BaseCombinator):
    """A combinator using weighted average
    """
    
    def _combine(self, combination_elements, ResultClass):
        """See the base class for documentation"""
        
        if not combination_elements:
            raise CombinatorError("No combination_elements given")
        
        # count the average and concatenation of the descriptions
        combination_elements.sort(key=lambda el: el.get_expectancy(), reverse=True)  
        avgexp = sum([ce.get_expectancy() for ce in combination_elements]) / len(combination_elements)
        desc = ' '.join([ce.get_description() for ce in combination_elements])                    
            

        return ResultClass(expectancy=avgexp, description=desc)
