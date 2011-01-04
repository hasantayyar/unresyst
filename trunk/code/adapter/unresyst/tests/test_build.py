"""Tests for the building phase"""

from nose.tools import eq_
from django.db.models import Q

from unresyst import Recommender
from unresyst.models.common import SubjectObject, Recommender as RecommenderModel
from unresyst.models.abstractor import PredictedRelationshipDefinition, \
    RelationshipInstance, RuleInstance, RuleRelationshipDefinition
from unresyst.models.aggregator import AggregatedRelationshipInstance    
from test_base import TestBuild, TestEntities

from demo.recommender import ShoeRecommender
from demo.models import User, ShoePair

#TODO: otestovat cascade delete na recommenderu


class TestRecommender(TestBuild):
    """Test case for the recommender class"""
    
    def test_recommender_created(self):
        """Test that the recommender was created during the build"""        
        
        # get it from db
        rec = RecommenderModel.objects.filter(
            class_name=ShoeRecommender.__name__)
        
        # assert there's one            
        eq_(rec.count(), 1, "There should be right one recommender %s." \
            % ShoeRecommender.name)
        
        rec = rec[0]
        
        # assert it has the right name
        eq_(rec.name, ShoeRecommender.name)
        
        # assert the subjects != objects
        eq_(rec.are_subjects_objects, \
            ShoeRecommender.subjects == ShoeRecommender.objects)
        
        # assert the model is saved in the recommender
        eq_(ShoeRecommender.recommender_model, rec)            


class TestAbstractor(TestEntities):
    """Testing the abstractor in the build phase"""  
        
    # creating subjectobjects:
    #
    
    def test_create_subjectobjects(self):
        """Test creating universal subjects, objects"""
        
        # get the specific entities
        subjects = User.objects.all()
        objects = ShoePair.objects.all()
        
        universal = SubjectObject.objects.all()
        
        # assert the counts fit
        eq_(subjects.count() + objects.count(), universal.count())
        
        # assert all subjects and objects are there
        for entities, entity_type in ((subjects, 'S'), (objects, 'O')):
            for en in entities:

                # the universal representation of entity
                en_un = universal.filter(id_in_specific=en.id, entity_type=entity_type)
                
                # assert there's one            
                eq_(en_un.count(), 1, "There should be right one represenation" + \
                     "of %s, there are %d" % (en, en_un.count()))
                
                en_un = en_un[0]     
                
                # assert it has the right properties                 

                # name
                eq_(en_un.name, en.__unicode__())
                
                # recommender
                eq_(en_un.recommender.class_name, ShoeRecommender.__name__)

    
    # predicted relationship
    #                   
    
    def test_create_predicted_relationship_definition(self):
        """Test creating the definition of the predicted relationship"""
        
        # get definitions related to the shoe recommender
        qs = PredictedRelationshipDefinition.remove_subclass_objects().filter(
            recommender=ShoeRecommender.recommender_model)
        
        # get how many definitions there are
        # should be one
        eq_(qs.count(), 1)
        
        definition = qs[0]
        
        # test it has the right name
        eq_(definition.name, "User likes shoes.")

                                
    EXPECTED_PREDICTED_RELATIONSHIP_INSTANCES = (
            ('Alice', 'Sneakers', "User Alice likes shoes Sneakers."),
            ('Bob', 'Sneakers', "User Bob likes shoes Sneakers."),
    ) 

    
    def test_create_predicted_relationship_instances(self):
        """Test creating instances of the predicted relationship."""
        
        # get the relationship definition
        definition = PredictedRelationshipDefinition.remove_subclass_objects().get( 
            recommender=ShoeRecommender.recommender_model)
        
        # get instances of the predicted relationship
        instances = RelationshipInstance.remove_subclass_objects().filter(definition=definition)
        
        for expected_data in self.EXPECTED_PREDICTED_RELATIONSHIP_INSTANCES:

            # instances that have either one or another order of the subjobjects
            rel_instance = instances.filter(
                Q(subject_object1=self.universal_entities[expected_data[0]], 
                    subject_object2=self.universal_entities[expected_data[1]]) | \
                Q(subject_object1=self.universal_entities[expected_data[1]], 
                    subject_object2=self.universal_entities[expected_data[0]])
            )
                      
            # there should be one
            eq_(rel_instance.count(), 1)
                
            instance = rel_instance[0]
            
            # test it has the right description
            eq_(instance.description, expected_data[2])                


    # relationships:
    #

    def test_create_relationship_definitions(self):
        """Test creating the definitions of the relationships"""
        
        self._test_definitions(ShoeRecommender.relationships)

    
    EXPECTED_RELATIONSHIP_DICT = {
        # relationship name, list of instances - (entity1, entity2, description)
        # for symmetric relationships the description is a pair - both orderings
        "User has viewed shoes.": (
            ('Alice', 'Rubber Shoes', "User Alice has viewed Rubber Shoes."),
            ('Bob', 'Sneakers', "User Bob has viewed Sneakers."),
            ('Cindy', 'Rubber Shoes', "User Cindy has viewed Rubber Shoes."),
        ),
        "Users live in the same city.": (
            ('Alice', 'Bob', ("Users Alice and Bob live in the same city.",
                "Users Bob and Alice live in the same city.")),
        ),
        "Shoes were made by the same manufacturer.": (
            ('Sneakers', 'Rubber Shoes', 
                ("Shoes Sneakers and Rubber Shoes were made by the same manufacturer.",
                "Shoes Rubber Shoes and Sneakers were made by the same manufacturer.")),
        ),
        'User lives in the same city as the shoe manufacturer.': (
            ('Alice', 'Rubber Shoes', "User Alice is from the same city as manufacturer of Rubber Shoes."),
            ('Bob', 'Rubber Shoes',  "User Bob is from the same city as manufacturer of Rubber Shoes."),
            ('Alice', 'Sneakers',  "User Alice is from the same city as manufacturer of Sneakers."),
            ('Bob', 'Sneakers', "User Bob is from the same city as manufacturer of Sneakers."),
            ('Cindy', 'RS 130', "User Cindy is from the same city as manufacturer of RS 130."),
        ),
    }
        
                                
    def test_create_relationship_instances(self):
        """Test creating instances of all the defined relationships."""
        
        self._test_instances(
            def_list=ShoeRecommender.relationships,
            expected_dict=self.EXPECTED_RELATIONSHIP_DICT,
            instance_manager=RelationshipInstance.objects)    
    
    # rules:
    #
    
    def test_create_rule_definitions(self):
        """Test creating the definitions of the rules"""
        
        self._test_definitions(ShoeRecommender.rules)


    EXPECTED_RULE_DICT = {
        # rule name, list of instances - (entity1, entity2, description, expectancy)
        # for symmetric rules the description is a pair - both orderings
        "Don't recommend winter shoes for southern users.": (
            ('Alice', 'RS 130', "Alice is from south, so RS 130 can't be recommended to him/her.", 1),
            ('Bob', 'RS 130', "Bob is from south, so RS 130 can't be recommended to him/her.", 1),
        ),
        "Users with similar age.": (
            ('Alice', 'Bob', ("Users Alice and Bob are about the same age.", 
                "Users Bob and Alice are about the same age."), 0.75),
        ),
        "Shoes with common keywords.": (
            ('Rubber Shoes', 'Sneakers', ("The shoe pairs Rubber Shoes and Sneakers share some keywords.",
                "The shoe pairs Sneakers and Rubber Shoes share some keywords."), 1),
            ('Sneakers', 'RS 130', ("The shoe pairs Sneakers and RS 130 share some keywords.",
                "The shoe pairs RS 130 and Sneakers share some keywords."), 0.5),                
        ),
    }            

    def test_create_rule_instances(self):
        """Test creating instances of all the defined rules."""
        
        self._test_instances(
            def_list=ShoeRecommender.rules,
            expected_dict=self.EXPECTED_RULE_DICT,
            instance_manager=RuleInstance.objects)
            
    # auxiliary functions:
    # 
    
    def _test_instances(self, def_list, expected_dict, instance_manager):
        """Test creating instances.
        
        @type def_list: list of Rule/Relationship definitions    
        @param def_list: a list of definitions to check
        
        @type expected_dict: dict str: tuple
        @param expected_dict: dictionary of expected instance attributes
        
        @type instance_manager: django.db.models.manager.Manager
        @param instance_manager: the manager above rule/relationship instances
        """
        # get definitions related to the shoe recommender
        qs = RuleRelationshipDefinition.objects.filter(
            recommender=ShoeRecommender.recommender_model)                
        
        # for each defined type there should be a model definition in db
        for r in def_list:

            # get the expected data
            expected_relationships = expected_dict[r.name]                        

            # get the definition model by name (shouldn't throw an error)
            definition = qs.get(name=r.name)
            
            instances = instance_manager.filter(definition=definition)
            
            # expect there are as many relationship instances as expected
            eq_(instances.count(), len(expected_relationships))
            
            for expected_data in expected_relationships:
            
                # instances that have either one or another order of the subjobjects
                rel_instance = instances.filter(
                    Q(subject_object1=self.universal_entities[expected_data[0]], 
                        subject_object2=self.universal_entities[expected_data[1]]) | \
                    Q(subject_object1=self.universal_entities[expected_data[1]], 
                        subject_object2=self.universal_entities[expected_data[0]])
                )
                          
                # there should be one
                eq_(rel_instance.count(), 1)
                    
                instance = rel_instance[0]
            
                # test it has the right description
                # the diferentiation for symmetric relationships - the order 
                # of the entities in the description can be arbitrary
                if r.is_symmetric:
                    desc_tuple = expected_data[2]
                    assert instance.description == desc_tuple[0] or \
                        instance.description == desc_tuple[1], \
                            "The description '%s' is wrong. Should be '%s' or '%s'" % \
                            (instance.description, desc_tuple[0], desc_tuple[1])
                else:
                    eq_(instance.description, expected_data[2]) 
                    
                # for rules    
                if len(expected_data) == 4:
                    eq_(instance.confidence, expected_data[3])
                    

    def _test_definitions(self, def_list):
        """Test the definitions.
        
        @type def_list: an iterable of RuleRelationshipDefinition model
        @param def_list: list of definitions to check.
        """
        # get definitions related to the shoe recommender
        qs = RuleRelationshipDefinition.objects.filter(
            recommender=ShoeRecommender.recommender_model)
        
        # assert the number of definitions is right
        eq_(qs.count(), len(ShoeRecommender.relationships) + len(ShoeRecommender.rules))
        
        # for each defined type there should be a model definition in db
        for r in def_list:

            # get the definition model by name (shouldn't throw an error)
            rmodel = qs.get(name=r.name)
            
            # assert the positiveness, weight and relationship type are right
            eq_(rmodel.is_positive, r.is_positive)
            eq_(rmodel.weight, r.weight)   
            eq_(rmodel.relationship_type, r.relationship_type)      

def _count_exp(conf):
    return 0.5 + conf/2
    
def _count_neg_exp(conf):    
    return 0.5 - conf/2
                
class TestAggregator(TestEntities):
    """Testing the building phase of the Linear Aggregator"""
    
    EXPECTED_AGGREGATES = {
        # S-O
        ('Alice', 'RS 130'): (_count_neg_exp(0.85), 'S-O'), # 0.075
        ('Alice', 'Rubber Shoes'): ((_count_exp(0.4) + _count_exp(0.1))/2, 'S-O'), # 0.625
        ('Alice', 'Sneakers'): (_count_exp(0.1), 'S-O'), # 0.55
        ('Bob', 'RS 130'): (_count_neg_exp(0.85), 'S-O'), # 0.075
        ('Bob', 'Sneakers'): ((_count_exp(0.4) + _count_exp(0.1))/2, 'S-O'), # 0.625
        ('Bob', 'Rubber Shoes'): (_count_exp(0.1), 'S-O'), # 0.55
        ('Cindy', 'Rubber Shoes'): (_count_exp(0.4), 'S-O'), # 0.7
        ('Cindy', 'RS 130'): (_count_exp(0.1), 'S-O'), # 0.55
        
        # S-S
        ('Alice', 'Bob'): ((_count_exp(0.75 * 0.2) + _count_exp(0.3))/2, 'S-S'), # 0.6125
        
        # O-O
        ('Rubber Shoes', 'Sneakers'): ((_count_exp(0.4) + _count_exp(0.1))/2, 'O-O'), # 0.625
        ('Sneakers', 'RS 130'): (_count_exp(0.2), 'O-O'), # 0.6        
    }
    """A dictionary: pair of entities : expectancy."""

    def test_aggregates_created(self):
        """Test that the aggregates were created as expected"""
        
        # filter aggregated instances for my recommender
        aggr_instances = AggregatedRelationshipInstance.objects.filter(
                            recommender=ShoeRecommender.recommender_model)
        
        # assert it has the expected length 
        eq_(aggr_instances.count(), len(self.EXPECTED_AGGREGATES))
        
        for aggr_inst in aggr_instances.iterator():
            pair1 = (aggr_inst.subject_object1.name, aggr_inst.subject_object2.name)
            pair2 = (aggr_inst.subject_object2.name, aggr_inst.subject_object1.name)            
            
            # try getting the instance from expected in both directions
            if self.EXPECTED_AGGREGATES.has_key(pair1):
                expected_expectancy, expected_rel_type = self.EXPECTED_AGGREGATES[pair1]
            else:
                if self.EXPECTED_AGGREGATES.has_key(pair2):
                    expected_expectancy,expected_rel_type = self.EXPECTED_AGGREGATES[pair2]
                else:
                    # if not found it's unexpected.
                    assert False, \
                        "Unexpected aggregate between '%s' and '%s' expectancy: %f" % \
                        (pair1 + (aggr_inst.expectancy, ))

            # assert the expectancy is as expected    
            eq_(aggr_inst.expectancy, expected_expectancy,
                "Expectancy is '%f' should be '%f' for the pair %s, %s" % \
                    ((aggr_inst.expectancy, expected_expectancy) + pair1)) 
        
            # assert the relationship type is as expected    
            eq_(aggr_inst.relationship_type, expected_rel_type,
                "Relationship type is '%s' should be '%s' for the pair %s, %s" % \
                    ((aggr_inst.relationship_type, expected_rel_type) + pair1)) 
                            
        
