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
        print "  Compiling aggregates."
        
        # for available aggregates create an instance with the aggregated result
        # 
        self.compilator.compile_aggregates(recommender_model)
        
        print "  Done. Compiling similar objects."
        
        # if subjects == objects
        if recommender_model.are_subjects_objects:

            # take similar on both sides
            self.compilator.compile_similar_subjectobjects(recommender_model)

        else:
        
            # take similar to the ones we already have (content-based recommender)
            self.compilator.compile_similar_objects(recommender_model)
            print "  Done. Compiling similar subjects."

            # take liked objects of similar users (almost collaborative filtering)
            self.compilator.compile_similar_subjects(recommender_model)                
        

        print "Predictions compiled. Compiling the inner algorithm..."
        
        super(CompilingAlgorithm, self).build(recommender_model=recommender_model)        
