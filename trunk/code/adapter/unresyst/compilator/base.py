"""The base class for all compilators BaseCompilator"""

class BaseCompilator(object):
    """The base class for all compilators"""
    
    def __init__(self, combinator):
        """The initializer"""

        self.combinator = combinator
        """The combinator that should be used during compiling"""        

    def compile_all(self, recommender_model):
        """Compile preferences, known relationships + similarities.        
        """
        pass
        

