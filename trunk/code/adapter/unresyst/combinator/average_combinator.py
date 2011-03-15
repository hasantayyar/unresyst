"""Combinator using a weighted average."""

from base import BaseCombinator

class AverageCombinator(BaseCombinator):
    """A combinator using weighted average
    """
    
    def _combine(self, combination_elements, ResultClass):
        """See the base class for documentation"""
        

        
        # count the average and concatenation of the descriptions
        combination_elements.sort(key=lambda el: el.get_expectancy(), reverse=True)  
        avgexp = sum([ce.get_expectancy() for ce in combination_elements]) / len(combination_elements)
        desc = self._concat_descriptions(combination_elements)
            
        return ResultClass(expectancy=avgexp, description=desc)
