"""A module for recommender making predictions in an outside engine"""
import csv

from base import BaseRecommender
from predictions import RelationshipPrediction
from unresyst.exceptions import RecommenderError, RecommenderNotBuiltError
from unresyst.models.algorithm import ExternalPrediction
from unresyst.models.common import Recommender as RecommenderModel

class ExternalRecommender(BaseRecommender):
    """A class representing an outside-world recommender with an Unresyst 
    interface.
    """
    
    PredictionModel = ExternalPrediction
    """The model where predictions are stored""" 
    
    
    # build phase:
    #
        
    @classmethod
    def build(cls):
        """Raise an error, as thist can't be done here, but outside.
        
        @raise RecommenderError: always
        """
        raise RecommenderError("The method is invalid for the external" + \
            " recommender. Call the export_data, build it outside and " + \
            "import_predictions.", cls)


    @classmethod
    def export_data(cls, filename):
        """Export the data from subject and object managers to a csv 
        file of the given name.
        
        @type filename: str
        @param filename: the full path to the file
        
        @raise FileNotExists and other file open errors.
        """
        
        with open(filename, 'w') as f:
                
            # export the relationships to the given file
            cls.predicted_relationship.export(f)
        
    @classmethod
    def import_predictions(cls, filename):
        """Loads predictions from the given csv file.
        
        Creates the recommender model for the recommender and imports the 
        predictions from the given file. The file has to be in format:
        <id subject>,<id object>,<prediction>\n
        
        @type filename: str
        @param filename: the full path to the file

        @raise FileNotExists and other file open errors.
        """
        
        cls._print('Deleting old predictions...')
        
        
        # if the recommender with the given name exists, delete it,
        RecommenderModel.objects.filter(class_name=cls.__name__).delete()
        
        # create a new recommender and save it
        recommender_model = RecommenderModel(
            class_name=cls.__name__,
            name=cls.name,
            is_built=False,
            are_subjects_objects=False
        )        
        recommender_model.save() 
        
        # open the csv reader
        reader = csv.reader(open(filename, "rb"), delimiter=',', quoting=csv.QUOTE_NONE)
        
        # parse the csv line by line
        for subj_id, obj_id, expectancy in reader:
            
            # parse the values to the right types
            subj_id = int(subj_id)
            obj_id = int(obj_id)
            expectancy = float(expectancy)
            
            # create a prediction
            cls.PredictionModel.objects.create(
                subj_id=subj_id,
                obj_id=obj_id,
                recommender=recommender_model,
                expectancy=expectancy
            )
        
        recommender_model.is_built=True
        recommender_model.save()            

                
    # recommend phase
    #
    @classmethod        
    def predict_relationship(cls, subject, object_):
        """See the base class for the explanation

        If the prediction doesn't exist retruns None.
        """

        recommender_model = cls._get_recommender_model()
        
        # if the recommender isn't built raise an error
        if not recommender_model or not recommender_model.is_built:
            raise RecommenderNotBuiltError(
                message="Build the recommender prior to performing the " + \
                    "predict_relationship action.",
                recommender=cls
            )
        
        # get the prediction if it exists
        qs_prediction_model = cls.PredictionModel.objects.filter(
            recommender=recommender_model,
            subj_id=subject.pk,
            obj_id=object_.pk
        )
        
        # if not return none
        if not qs_prediction_model:
            return None
        
        # if so extract the expectancy
        assert qs_prediction_model.count() == 1        
        expectancy = qs_prediction_model[0].expectancy
        
        # create and return the outer-world object
        prediction = RelationshipPrediction(
            subject=subject,
            object_=object_,
            expectancy=expectancy
        )            
        return prediction


    @classmethod
    def get_recommendations(cls, subject, count=None):        
        """For documentation, see the base class"""
        
        recommender_model = cls._get_recommender_model()
        
        # if the recommender isn't built raise an error
        if not recommender_model or not recommender_model.is_built:
            raise RecommenderNotBuiltError(
                message="Build the recommender prior to performing the " + \
                    "get_recommendations action.",
                recommender=cls
            )
        
        # if count wasn't given take the default one
        if not count:
            count = cls.default_recommendation_count
        
        # get the prediction objects
        qs_predictions = cls.PredictionModel.objects.filter(
            subj_id=subject.pk,
            recommender=recommender_model)\
            .order_by('-expectancy')[:count]
        
        recommendations = []
        
        # go through the obtained predictions
        for pred_model in qs_predictions:

            # get the object by the id
            object_=cls.objects.get(pk=pred_model.obj_id)
                        
            # create the outer-world object
            prediction = RelationshipPrediction(
                subject=subject,
                object_=object_,
                expectancy=pred_model.expectancy
            )            
            
            recommendations.append(prediction)

        return recommendations
                    
   
    
   

