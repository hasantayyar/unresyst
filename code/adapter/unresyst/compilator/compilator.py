"""The basic compilator used in Unresyst"""

from base import BaseCompilator
from unresyst.constants import *
from unresyst.models.aggregator import AggregatedRelationshipInstance
from unresyst.models.abstractor import RelationshipInstance
from unresyst.models.algorithm import RelationshipPredictionInstance

class Compilator(BaseCompilator):
    
    def __init__(self, combinator, depth=DEFAULT_COMPILATOR_DEPTH, breadth=DEFAULT_COMPILATOR_BREADTH):
        """The initializer"""    
        
        super(Compilator, self).__init__(combinator=combinator)
        
        self.depth = depth
        """The depth until where the comiplates should be done"""
        
        self.breadth = breadth
        """The number of neighbours that will be taken during the compilation"""


    def compile_all(self, recommender_model):
        """Compile preferences, known relationships + similarities.
        """
        #TODO pryc:
        self.compile_aggregates(recommender_model)

        print "  Compiling similar objects."
        
        # if subjects == objects
        if recommender_model.are_subjects_objects:

            # take similar on both sides
            self._mark_similar_subjectobjects(recommender_model)

        else:
        
            # take similar to the ones we already have (content-based recommender)
            self._mark_similar_objects(recommender_model)
            print "  Done. Compiling similar subjects."

            # take liked objects of similar users (almost collaborative filtering)
            self._mark_similar_subjects(recommender_model)   
            
        # after the marks have been made, pass it all to the combinator
        #TODO zavolat combinator.            

    #TODO pryc, asi nebude potreba
    def compile_aggregates(self, recommender_model):
        """Create predictions from aggregates"""        
        
        # filter only S-O or SO-SO aggregates
        #
        rel_type = RELATIONSHIP_TYPE_SUBJECTOBJECT_SUBJECTOBJECT \
            if recommender_model.are_subjects_objects else \
                RELATIONSHIP_TYPE_SUBJECT_OBJECT 
        
        qs_aggr = AggregatedRelationshipInstance.objects.filter(
                    recommender=recommender_model,
                    relationship_type=rel_type)

        # go through the aggregates, create predictions and save them
        for aggr in qs_aggr.iterator():

            # order the arguments as they should be    
            so1, so2 = self._order_in_pair(aggr.subject_object1, aggr.subject_object2)

            prediction = RelationshipPredictionInstance(
                            subject_object1=so1,
                            subject_object2=so2,
                            description=aggr.description,
                            expectancy=aggr.expectancy,
                            recommender=recommender_model)
                            
            prediction.save()                            
        
        print "    %d aggregated predictions created" % qs_aggr.count()
                            
    
    def _mark_similar_objects(self, recommender_model):
        """Create predictions by adding objects similar to ones the objects
        in predicted_relationship - that's a content-based recommender
        """   
        
        self._mark_similar_entities(
                recommender_model=recommender_model,
                start_entity_type=ENTITY_TYPE_SUBJECT)
    
    def _mark_similar_subjects(self, recommender_model):
        """Create predictions by adding objects that similar subjects liked
        - that's collaborative filtering
        """                
        
        self._mark_similar_entities(
                recommender_model=recommender_model,
                start_entity_type=ENTITY_TYPE_OBJECT)


    def _mark_similar_subjectobjects(self, recommender_model):
        """Create predictions based on similarity for recommenders where 
        subjects==objects
        """
        
        # firstly the normal direction
        self._mark_similar_entities(
                recommender_model=recommender_model,
                start_entity_type=ENTITY_TYPE_SUBJECTOBJECT,
                reverse=False)
        
        # secondly the opposite
        self._compile_similar_entities(
                recommender_model=recommender_model,
                start_entity_type=ENTITY_TYPE_SUBJECTOBJECT,
                reverse=True)

    def _order_in_pair(self, arg1, arg2):
        """Swap the arguments in the rule/relationships so that the first
        has a lower id than the second (for subjectobjects), or the subject
        is the first (for others)
        """
        # for subjectobject return ordered by pk
        if arg1.entity_type == ENTITY_TYPE_SUBJECTOBJECT:
            if arg2.pk < arg1.pk:
                return (arg2, arg1)
            return (arg1, arg2)
        # for others return subject first            
        if arg2.entity_type == ENTITY_TYPE_SUBJECT:
            return (arg2, arg1)
        return (arg1, arg2)

    SIMILARITY_RELATIONSHIP_TYPES = {
        ENTITY_TYPE_SUBJECT: RELATIONSHIP_TYPE_OBJECT_OBJECT,
        ENTITY_TYPE_OBJECT: RELATIONSHIP_TYPE_SUBJECT_SUBJECT,
        ENTITY_TYPE_SUBJECTOBJECT: RELATIONSHIP_TYPE_SUBJECTOBJECT_SUBJECTOBJECT
    }            
    """Dictionary entity type: relationship entity type.
    Key is the entity type where the traversing for similarity starts, value
    is the relationship type that should be traversed for similarity.
    """
    
    ORDERING = {
        ENTITY_TYPE_OBJECT: "subject_object1__pk",
        ENTITY_TYPE_SUBJECT: "subject_object2__pk",
        ENTITY_TYPE_SUBJECTOBJECT: "subject_object1__pk",
    }
    """Dictinary entity type (starting) - name of the attribute in PredictedRelationship, 
    that should be used for sorting"""
    
    
    def _mark_similar_entities(self, recommender_model, start_entity_type, reverse=False):
        """Create predictions from start_entity_type objects, looking for 
        similar entities in end_entity_type
        
        @type recommender_model: models.common.Recommender
        @param recommender_model: the model the for which the predictions
            should be built

        @type start_entity_type: str
        @param start_entity_type: the entity type, where to start searching for
            similar entities. E.g. if start_entity_type is 'S', similar 'O' 
            will be added to predictions to each 'S'.

        @type reverse: bool
        @param reverse: relevant only if start_entity_type=='SO', indicates 
            whether the relationships will be traversed in the reverse order.            
        """            
        
        # get the predictions for this recommender
        qs_predictions = RelationshipPredictionInstance.objects.filter(
                            recommender=recommender_model)

        ordering = self.ORDERING[start_entity_type]
                   
        # go through the predicted relationship instances 
        # (objects that subjects liked)
        # ordered as needed
        qs_pred_rel_instances = RelationshipInstance\
            .filter_predicted(recommender_model)\
            .order_by(ordering)\
            .select_related(depth=1)
        
        # the caching variable    
        last_fin = None       
        last_qs = None         
        
        print "Predicted relationship count: %d" % qs_pred_rel_instances.count()
        
        i = 0
        
        # count neighbourhood
        count_n = 0
        
        # count all        
        count_all = 0
        
        for pred_inst in qs_pred_rel_instances.iterator():
            
            i += 1
            # get the subject and object from the relationship instance
            start, fin = (pred_inst.subject_object1, pred_inst.subject_object2) \
                if pred_inst.subject_object1.entity_type == start_entity_type \
                else (pred_inst.subject_object2, pred_inst.subject_object1)
            
            # if they are subjectobjects and reversed swap them
            if start_entity_type == ENTITY_TYPE_SUBJECTOBJECT and reverse:
                start, fin = fin, start
            
            similarity_relationship_type = self.SIMILARITY_RELATIONSHIP_TYPES[start_entity_type]
            
            # if the ending entity is the same as the last time, use the cached qs
            if last_fin == fin:
                qs_similar_rels = last_qs
            else:                
                # get objects similar to obj (whole relationships) - only breadth highest
                qs_similar_rels = AggregatedRelationshipInstance\
                    .get_relationships(fin)\
                    .filter(relationship_type=similarity_relationship_type)\
                    .order_by('-expectancy')
                
                # current count of theoretically available predictions
                cur_count_all = qs_similar_rels.count()
                
                qs_similar_rels = qs_similar_rels[:self.breadth]\
                    .select_related(depth=1)

            # keep it for the next time
            last_fin = fin
            last_qs = qs_similar_rels
            

            count = qs_similar_rels.count()

            count_all += cur_count_all
            count_n += count
            
            if count and i % 1000 == 0:
                print "similar count: %d; relationships processed: %d" % (count, i)
                import gc; gc.collect()
            
            # go through them 
            for similar_rel in qs_similar_rels.iterator():
            
                # get the object similar to obj from the relationship
                similar_fin = similar_rel.get_related(fin)

                # find out whether there exists a prediction for the pair
                qs_pair_predictions = RelationshipPredictionInstance\
                                        .filter_relationships(
                                            object1=start,
                                            object2=similar_fin,
                                            queryset=qs_predictions)

                # if exists, keep it there, ignore
                if qs_pair_predictions.exists():
                    continue
                
                # order the arguments as they should be    
                so1, so2 = self._order_in_pair(start, similar_fin)                    

                # if not, create it with the attributes of the similarity 
                # relationship instance
                prediction = RelationshipPredictionInstance(
                            subject_object1=so1,
                            subject_object2=so2,
                            description=similar_rel.description,
                            expectancy=similar_rel.expectancy,
                            recommender=recommender_model)
                            
                prediction.save()                                 
                    
        print "For starting entity type %s, %d out of %d possible relationships created" \
                 % (start_entity_type, count_n, count_all)
