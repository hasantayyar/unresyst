"""Combinator using the magic function."""

from base import BaseCombinator

class FunctionCombinator(BaseCombinator):
    """A combinator using a special function to combine.
    """
    
    def _combine(self, combination_elements, ResultClass):
        """See the base class for documentation"""
        
        # narvat to do magicke funkce a hotovka (spocitat prumer a pocet positive, negative)
        res = ResultClass(expectancy=1, description='')
        return res
