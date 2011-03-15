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

        
    def get_relationship_prediction(self, recommender_model, dn_subject, dn_object, remove_predicted):
        """See the base class for the documentation.
        """
        
        # get what we have from the inner algo
        inner_prediction = super(CompilingAlgorithm, self).get_relationship_prediction(
                            recommender_model=recommender_model,
                            dn_subject=dn_subject,
                            dn_object=dn_object,
                            remove_predicted=remove_predicted)
        
        # if it's trivial, than return it
        if remove_predicted and inner_prediction.is_trivial:
            return inner_prediction
        
        # if it's not uncertain, it was already available for the inner algorithm,
        # return it
        if not inner_prediction.is_uncertain:
            return inner_prediction
            
        # otherwise compile the prediction from all available info 
        prediction = self.compilator.compile_prediction(
            recommender_model=recommender_model,
            dn_subject=dn_subject,
            dn_object=dn_object)

        # if it found something, return it            
        if prediction:        
            return prediction
            
        # otherwise return the uncertain
        return self._get_uncertain_prediction(
                recommender_model=recommender_model, 
                dn_subject=dn_subject, 
                dn_object=dn_object
            )                    
