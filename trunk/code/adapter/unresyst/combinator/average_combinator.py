"""Combinator using a weighted average."""

from base import BaseCombinator

class AverageCombinator(BaseCombinator):
    """A combinator using weighted average
    """
    
    def _combine(self, combination_elements, ResultClass):
        """See the base class for documentation"""
                                
        # sort it in order to provide the right order of explanations
        combination_elements.sort(key=lambda el: el.get_expectancy(), reverse=True)  

        # count the average and concatenation of the descriptions
        avgexp = sum([ce.get_expectancy() for ce in combination_elements]) / len(combination_elements)
        desc = self._concat_descriptions(combination_elements)
            
        return ResultClass(expectancy=avgexp, description=desc)
