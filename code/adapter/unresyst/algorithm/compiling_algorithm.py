"""The CompilingAlgorithm class"""

from base import BaseAlgorithm

class CompilingAlgorithm(BaseAlgorithm):
    """The algorithm that compiles aggregated similarities and biases with
    the predictions.
    """
    def __init__(self, inner_algorithm, compilator):
        """The initializer"""
                
        super(CompilingAlgorithm, self).__init__(inner_algorithm=inner_algorithm)
        
        self.compilator=compilator
        """The compilator that will be used during the build"""

    def build(self, recommender_model):
        """See the base class for documentation.
        
        Compiles and calls the inner algorithm build
        """        
        print "  Compiling aggregates and predictions."
        
        self.compilator.compile_all(recommender_model)             
        

        print "Predictions compiled. Building the inner algorithm..."
        
        super(CompilingAlgorithm, self).build(recommender_model=recommender_model)        
