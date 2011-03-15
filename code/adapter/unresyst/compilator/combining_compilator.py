"""The combining compilator class"""

from base import BaseCompilator
from unresyst.constants import *
from unresyst.models.common import SubjectObject

class CombiningCompilator(BaseCompilator):
    """The compilator using the given combinator to combine the predictions
    that it reveals
    """        
    
    def __init__(self, combinator, depth=DEFAULT_COMPILATOR_DEPTH, breadth=DEFAULT_COMPILATOR_BREADTH):
        """The initializer, combinator is not optional."""    
        
        super(CombiningCompilator, self).__init__(combinator=combinator, depth=depth, breadth=breadth)
        
    def compile_prediction(self, recommender_model, dn_subject, dn_object):
        """Create a prediction using all available information and our combinator.
        
        @type recommender_model: models.common.Recommender
        @param recommender_model: the recommender model
        
        @type dn_subject: SubjectObject
        @param dn_subject: the domain neutral subject
        
        @type dn_object: SubjectObject
        @param dn_object: the domain neutral object
        
        @rtype: RelationshipPredictionInstance
        @return: the prediction from what we know, if we don't know anything return None.
        """
        # find all we know about the subject - object pair - biases, similarities, clusters,...                
        els = self.get_pair_combination_elements(dn_subject=dn_subject, dn_object=dn_object)
        
        if not els:
            return None
            
        # pass it all to the combinator to get the prediction
        pred = self.combinator.combine_pair_prediction_elements(combination_elements=els)

        # fill the missing fields in the prediction and save
        pred.recommender = recommender_model
        pred.subject_object1 = dn_subject
        pred.subject_object2 = dn_object
        return pred

    
    def compile_all(self, recommender_model):
        """Compile preferences, known relationships + similarities.
        """
        # go through the sujbects (or subjectobjects)
        #
        
        subject_ent_type = ENTITY_TYPE_SUBJECTOBJECT if recommender_model.are_subjects_objects \
                else ENTITY_TYPE_SUBJECT 
        
        qs_subjects = SubjectObject.objects.filter(
                        recommender=recommender_model, 
                        entity_type=subject_ent_type)
        
        for subj in qs_subjects.iterator():
            
            # get the most promising objects for the subject
            promising_objects = self.combinator.choose_promising_objects(
                                    dn_subject=subj, 
                                    min_count=self.depth)  
            
            # go through the promising objects
            for obj in promising_objects:
                
                # compile the predition and save it
                pred = self.compile_prediction(
                    recommender_model=recommender_model,
                    dn_subject=subj,
                    dn_object=obj)

                # if the compilate is empty, it's an error                    
                if not pred:
                    raise RecommenderBuildError(
                        message="Nothing found for the pair %s, %s, although the object was in promising." \
                            % (subj, obj),
                        recommender=recommender_model)
                                                            
                pred.save()
                
