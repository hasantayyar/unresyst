"""The twisted average combinator"""


from base import BaseCombinator

class TwistedAverageCombinator(BaseCombinator):
    """A combinator using weighted average
    """
    
    def _combine(self, combination_elements, ResultClass):
        """See the base class for documentation
        See the thesis text for the explanation of twisted average
        """
                        
        # number of positive elements
        num_positive = len(filter(lambda ce: ce.get_positiveness(), combination_elements))
        
        # the difference between the number of positive and negative
        pos_dif = abs(len(combination_elements) - 2 * num_positive)
        
        # the average expectancy
        avgexp = sum([ce.get_expectancy() for ce in combination_elements]) / len(combination_elements)
        
        # select the formula according to the expectancy
        if avgexp <= 0.5:
            res_exp = pow(2, pos_dif) * pow(avgexp, pos_dif + 1)
        else:
            res_exp = 1 - abs(pow(2, pos_dif) * pow((avgexp - 1), pos_dif + 1))

        # concat the description
        desc = self._concat_descriptions(combination_elements)
        
        # return the resulting class
        return ResultClass(expectancy=res_exp, description=desc)
