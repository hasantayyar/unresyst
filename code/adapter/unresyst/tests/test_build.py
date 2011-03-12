"""Tests for the building phase.

Each layer has a separate test:
 - recommender
 - abstractor
 - aggregator
 - algorithm 

The tests are always started by running the recommender.build method.
"""

from nose.tools import eq_, assert_raises, assert_almost_equal
from django.db.models import Q

from unresyst import Recommender
from unresyst.models.common import SubjectObject, Recommender as RecommenderModel
from unresyst.models.abstractor import PredictedRelationshipDefinition, \
    RelationshipInstance, RuleInstance, RuleRelationshipDefinition, ClusterSet, \
    BiasDefinition, ExplicitRuleDefinition, ExplicitRuleInstance
from unresyst.models.aggregator import AggregatedRelationshipInstance, AggregatedBiasInstance
from unresyst.models.algorithm import RelationshipPredictionInstance    
from test_base import TestBuild, TestEntities, DBTestCase
from unresyst.exceptions import ConfigurationError, DescriptionKeyError
from unresyst.recommender.rules import ExplicitSubjectObjectRule

from demo.recommender import ShoeRecommender
from demo.models import User, ShoePair

PLACES = 4
"""How many places are counted for expectancy accuracy"""

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
        eq_(ShoeRecommender._get_recommender_model(), rec)            

    def test_cascade_delete(self):
        """Test that the rebuild deletes all that should be deleted"""
        
        # get and delete alice
        a = User.objects.get(name='Alice')        
        a.delete()
        
        # build the recommender again
        ShoeRecommender.build()
        
        # assert there's nothing:
        
        # in SubjectObject
        eq_(SubjectObject.objects.filter(name='Alice').count(), 0)
        
        # in RelationshipInstance
        eq_(RelationshipInstance.objects.filter(subject_object1__name='Alice').count(), 0)
        eq_(RelationshipInstance.objects.filter(subject_object2__name='Alice').count(), 0)        
        
        # in RuleInstance
        eq_(RuleInstance.objects.filter(subject_object1__name='Alice').count(), 0)
        eq_(RuleInstance.objects.filter(subject_object2__name='Alice').count(), 0)
        
        # in AggregatedRelationshipInstance
        eq_(AggregatedRelationshipInstance.objects.filter(subject_object1__name='Alice').count(), 0)
        eq_(AggregatedRelationshipInstance.objects.filter(subject_object2__name='Alice').count(), 0)
        
        # in RelationshipPredictionInstance
        eq_(RelationshipPredictionInstance.objects.filter(subject_object1__name='Alice').count(), 0)
        eq_(RelationshipPredictionInstance.objects.filter(subject_object2__name='Alice').count(), 0)        


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
            recommender=ShoeRecommender._get_recommender_model())
        
        # get how many definitions there are
        # should be one
        eq_(qs.count(), 1)
        
        definition = qs[0]
        
        # test it has the right name
        eq_(definition.name, "User likes shoes.")

                                
    EXPECTED_PREDICTED_RELATIONSHIP_INSTANCES = (
            ('Alice', 'Sneakers', "User Alice likes shoes Sneakers."),
            ('Bob', 'Sneakers', "User Bob likes shoes Sneakers."),
            ('Edgar', 'Rubber Shoes', "User Edgar likes shoes Rubber Shoes."),
    ) 

    
    def test_create_predicted_relationship_instances(self):
        """Test creating instances of the predicted relationship."""
        
        # get the relationship definition
        definition = PredictedRelationshipDefinition.remove_subclass_objects().get( 
            recommender=ShoeRecommender._get_recommender_model())
        
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
            ('Cindy', 'Daisy', ("Users Cindy and Daisy live in the same city.",
                 "Users Daisy and Cindy live in the same city.")),
        ),
        "Shoes were made by the same manufacturer.": (
            ('Sneakers', 'Rubber Shoes', 
                ("Shoes Sneakers and Rubber Shoes were made by the same manufacturer.",
                "Shoes Rubber Shoes and Sneakers were made by the same manufacturer.")),
        ),
        'User lives in the same city as the shoe manufacturer.': (
            ('Alice', 'Rubber Shoes', "User Alice is from the same city as the manufacturer of Rubber Shoes."),
            ('Bob', 'Rubber Shoes',  "User Bob is from the same city as the manufacturer of Rubber Shoes."),
            ('Alice', 'Sneakers',  "User Alice is from the same city as the manufacturer of Sneakers."),
            ('Bob', 'Sneakers', "User Bob is from the same city as the manufacturer of Sneakers."),
            ('Cindy', 'RS 130', "User Cindy is from the same city as the manufacturer of RS 130."),
            ('Daisy', 'RS 130', "User Daisy is from the same city as the manufacturer of RS 130.")
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
        
        # explicit rules are tested separately
        rules = filter(lambda r: r.__class__ != ExplicitSubjectObjectRule, ShoeRecommender.rules)
        self._test_definitions(rules)


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
            ('Edgar', 'Fionna', ("Users Edgar and Fionna are about the same age.", 
                "Fionna and Edgar are about the same age."), 1),
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

        # explicit rules are tested separately
        rules = filter(lambda r: r.__class__ != ExplicitSubjectObjectRule, ShoeRecommender.rules)
                
        self._test_instances(
            def_list=rules,
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
            recommender=ShoeRecommender._get_recommender_model())                
        
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
            recommender=ShoeRecommender._get_recommender_model()) 
        
        # explicit rules are tested separately
        rules = filter(lambda r: r.__class__ != ExplicitSubjectObjectRule, ShoeRecommender.rules)
        
        # assert the number of definitions is right
        eq_(qs.count(), len(ShoeRecommender.relationships) + len(rules))
        
        # for each defined type there should be a model definition in db
        for r in def_list:

            # get the definition model by name (shouldn't throw an error)
            rmodel = qs.get(name=r.name)
            
            # assert the positiveness, weight and relationship type are right
            eq_(rmodel.is_positive, r.is_positive)
            eq_(rmodel.weight, r.weight)   
            eq_(rmodel.relationship_type, r.relationship_type)      


    EXP_CLUSTER_SETS = {
        "Shoe category cluster set.": 
            (
                {'For Sports': (('RS 130', 1, "RS 130 belong to the For Sports category."), 
                    ("Octane SL", 1, "Octane SL belong to the For Sports category.")),
                'Casual': (("Design Shoes", 1, "Design Shoes belong to the Casual category."), 
                    ("Sneakers", 1, "Sneakers belong to the Casual category.")),},
                'O', 0.3),
    }
    """A dictionary: cluster set name: contained clusters, entity type, weight,
    the members: object name, confidence, description."""
    
    def test_clusters(self):
        """Test that the clusters are created as expected"""
        
        # get cluster sets from db
        cluster_sets = ClusterSet.objects.filter(
            recommender=ShoeRecommender._get_recommender_model())
        
        # assert there are as many as expected
        eq_(len(self.EXP_CLUSTER_SETS), cluster_sets.count())
        
        for cs in cluster_sets:

            # get the expected contents
            clusters, ent_type, weight = self.EXP_CLUSTER_SETS[cs.name]
                        
            eq_(ent_type, cs.entity_type)
            eq_(weight, cs.weight)
            eq_(len(clusters), cs.cluster_set.count())
            
            # go through the clusters
            for c in cs.cluster_set.all():

                 cluster_members = clusters[c.name]
                 
                 eq_(len(cluster_members), c.clustermember_set.count())
                 
                 for cm in c.clustermember_set.all():
                     # expect the combination of entity and confidence is 
                     # in the expected
                     assert (cm.member.name, cm.confidence, cm.description) in cluster_members, \
                        "The member '%s' with confidence '%f' and description '%s' isn't one of the expected %s" % (
                            cm.member, cm.confidence, cm.description, cluster_members)

    EXP_BIASES = {
        "Users liking many shoes.": 
            {
                'Alice': (0.333333, "User Alice likes many shoe pairs."),
                'Bob': (0.333333, "User Bob likes many shoe pairs."),
                'Edgar': (0.333333, "User Edgar likes many shoe pairs."),
            },
        "Popular shoes":
            {
                'Sneakers': (0.6666666, "Shoe pair Sneakers is popular"),
                'Rubber Shoes': (0.333333, "Shoe pair Rubber Shoes is popular"),
            },
    }
    """A dictionary: cluster set name: contained clusters, entity type, weight"""    
    
    def test_bias(self):
        """Test that biases were created as expected"""
        
        # get bias definitions from db
        bias_defs = BiasDefinition.objects.filter(
            recommender=ShoeRecommender._get_recommender_model())
        
        # assert there are as many as expected
        eq_(len(self.EXP_BIASES), bias_defs.count())
        
        for bias_def in bias_defs:
            
            # assert it's in the expected
            assert self.EXP_BIASES.has_key(bias_def.name)

            # get the expected contents            
            exp_biases = self.EXP_BIASES[bias_def.name]
            
            eq_(len(exp_biases), bias_def.biasinstance_set.count(), 
                "Wrong count for definition '%s' should be %s, is %s" % \
                (bias_def.name, exp_biases, bias_def.biasinstance_set.all()))
            
            # go through the instances connected to definition
            for bias in bias_def.biasinstance_set.all():
                
                # assert it's in the expected biases
                assert exp_biases.has_key(bias.subject_object.name)
                
                # assert the properties are as expected
                exp_conf, exp_desc = exp_biases[bias.subject_object.name]
                
                assert_almost_equal(exp_conf, bias.confidence, PLACES)
                eq_(exp_desc, bias.description)                        
    
    EXP_EXPLICIT_RULES = {
        "Shoe rating.": 
            {
                ('Alice', 'Design Shoes'): (0.8, "User Alice has rated Design Shoes."),
                ('Bob', 'Design Shoes'): (0.2, "User Bob has rated Design Shoes."),
            },
    }
                
    def test_explicit_rules(self):
        """Test the explicit rules and their definitions 
        were created as expected"""
        
        rule_defs = ExplicitRuleDefinition.objects.all()
        
        # expect the definition count fits
        eq_(len(self.EXP_EXPLICIT_RULES), rule_defs.count())
        
        for rule_def in rule_defs:
            
            # assert the def is there
            assert self.EXP_EXPLICIT_RULES.has_key(rule_def.name)
            
            # get its expected rules
            exp_rules = self.EXP_EXPLICIT_RULES[rule_def.name]
            
            rules = ExplicitRuleInstance.objects.filter(definition=rule_def)
            
            for rule in rules:
                
                # assert the pair is expected
                if exp_rules.has_key((rule.subject_object1.name, rule.subject_object2.name)):
                    exp_rule = exp_rules[(rule.subject_object1.name, rule.subject_object2.name)]
                elif exp_rules.has_key((rule.subject_object2.name, rule.subject_object1.name)):
                    exp_rule = exp_rules[(rule.subject_object2.name, rule.subject_object1.name)]
                else:
                    assert False, "The pair %s, %s isn't expected" \
                        % (rule.subject_object1.name, rule.subject_object2.name)
                
                assert_almost_equal(exp_rule[0], rule.expectancy, PLACES)
                eq_(exp_rule[1], rule.description)
                
                            
class TestAbstractorRecommenderErrors(DBTestCase):
    """Test various errors thrown by Abstractor and/or Recommender and/or Algorithm"""

    def test_invalid_relationship_weight(self):
        """Test if the exception is raised for a relatioship with invalid weight"""
                  
        # set some invalid weight, assert it throws the error         
        w = ShoeRecommender.relationships[1].weight 
        ShoeRecommender.relationships[1].weight = 1.5

        assert_raises(ConfigurationError, ShoeRecommender.build)

        # restore the original value
        ShoeRecommender.relationships[1].weight = w

         
    def test_invalid_rule_weight(self):
        """Test if the exception is raised for a rule with invalid weight"""
                          
        # set some invalid weight, assert it throws the error         
        w = ShoeRecommender.rules[2].weight 
        ShoeRecommender.rules[2].weight = 1.5

        assert_raises(ConfigurationError, ShoeRecommender.build)

        # restore the original value
        ShoeRecommender.rules[2].weight = w         


    def test_invalid_confidence(self):
        """Test if the exception is raised for a rule with invalid confidence"""
                  
        # set some invalid weight, assert it throws the error         
        c = ShoeRecommender.rules[0].confidence
        ShoeRecommender.rules[0].confidence = lambda a, b: 1.3

        assert_raises(ConfigurationError, ShoeRecommender.build)

        # restore the original value
        ShoeRecommender.rules[0].confidence = c

    def test_empty_predicted_relationship(self):
        """Test building a recommender with emtpy predicted relationship"""
        
        # save and delete the predicted_relationship
        pr = ShoeRecommender.predicted_relationship
        ShoeRecommender.predicted_relationship = None
        
        # assert it raises an error
        assert_raises(ConfigurationError, ShoeRecommender.build)
        
        # restore the original predicted_relationship
        ShoeRecommender.predicted_relationship = pr
        
    def test_empty_subjects(self):
        """Test building a recommender with empty subjects"""
        
        # delete all users
        User.objects.all().delete()
        
        # assert it raises an error
        assert_raises(ConfigurationError, ShoeRecommender.build)        

    def test_empty_objects(self):
        """Test building a recommender with empty objects"""
        
        # delete all shoes
        ShoePair.objects.all().delete()
        
        # assert it raises an error
        assert_raises(ConfigurationError, ShoeRecommender.build)   
        
    def test_rule_description_error(self):
        """Test building a recommender with strange rule description"""
        
        # save and mess up the description
        d = ShoeRecommender.rules[1].description        
        ShoeRecommender.rules[1].description = """Some messed %(crap)s description"""
        
        # assert it raises an error
        assert_raises(DescriptionKeyError, ShoeRecommender.build)   
        
        # restore the original 
        ShoeRecommender.rules[1].description = d

    def test_relationship_description_error(self):
        """Test building a recommender with strange relationship description"""
        
        # save and mess up the description
        d = ShoeRecommender.relationships[0].description        
        ShoeRecommender.relationships[0].description = """Some other messed %(other_crap)s description"""
        
        # assert it raises an error
        assert_raises(DescriptionKeyError, ShoeRecommender.build)   
        
        # restore the original 
        ShoeRecommender.relationships[0].description = d

    def test_no_key_description_error(self):
        """Test building a recommender with a description without keys"""
        
        # save and mess up the description
        d = ShoeRecommender.rules[2].description        
        ShoeRecommender.rules[2].description = """No-key description."""
        
        # assert it doesn't raise any error
        ShoeRecommender.build()
        
        # restore the original 
        ShoeRecommender.rules[2].description = d
        
    def test_empty_rules_rels(self):
        """Test building the recommender with empty rules and relationships"""
        
        # save and delete rules and relationships
        rules = ShoeRecommender.rules
        relationships = ShoeRecommender.relationships
        
        ShoeRecommender.rules = ()
        ShoeRecommender.relationships = ()
        
        # build it, test it doesn't freeze
        ShoeRecommender.build()        
        
        # restore
        ShoeRecommender.rules = rules
        ShoeRecommender.relationships = relationships
                     
def _count_exp(conf):
    return 0.5 + conf/2
    
def _count_neg_exp(conf):    
    return 0.5 - conf/2
                
class TestAggregator(TestEntities):
    """Testing the building phase of the Linear Aggregator"""
    
    EXPECTED_AGGREGATES = {
        # S-O
        ('Alice', 'RS 130'): (_count_neg_exp(0.85), 'S-O', 
            ("Alice is from south, so RS 130 can't be recommended to him/her.",)), # 0.075
        ('Alice', 'Rubber Shoes'): ((_count_exp(0.4) + _count_exp(0.1))/2, 'S-O',
            ('User Alice has viewed Rubber Shoes. User Alice is from the same city as the manufacturer of Rubber Shoes.',)), # 0.625
        ('Alice', 'Sneakers'): (_count_exp(0.1), 'S-O',  
            ("User Alice is from the same city as the manufacturer of Sneakers.",)), # 0.55
            
        ('Bob', 'RS 130'): (_count_neg_exp(0.85), 'S-O', 
            ("Bob is from south, so RS 130 can't be recommended to him/her.",)), # 0.075
        ('Bob', 'Rubber Shoes'): (_count_exp(0.1), 'S-O',
            ("User Bob is from the same city as the manufacturer of Rubber Shoes.",)), # 0.55
        ('Bob', 'Sneakers'): ((_count_exp(0.4) + _count_exp(0.1))/2, 'S-O',
            ("User Bob has viewed Sneakers. User Bob is from the same city as the manufacturer of Sneakers.",)), # 0.625

        ('Cindy', 'RS 130'): (_count_exp(0.1), 'S-O',
            ("User Cindy is from the same city as the manufacturer of RS 130.",)), # 0.55
        ('Cindy', 'Rubber Shoes'): (_count_exp(0.4), 'S-O',
            ("User Cindy has viewed Rubber Shoes.",)), # 0.7
        
        ('Daisy', 'RS 130'): (_count_exp(0.1), 'S-O',
            ("User Daisy is from the same city as the manufacturer of RS 130.",)), # 0.55
        
        # S-S
        ('Alice', 'Bob'): ((_count_exp(0.75 * 0.2) + _count_exp(0.3))/2, 'S-S', (
            "Users Alice and Bob live in the same city. Users Alice and Bob are about the same age.",
            "Users Alice and Bob live in the same city. Users Bob and Alice are about the same age.",
            "Users Alice and Bob live in the same city. Users Bob and Alice are about the same age.",
            "Users Bob and Alice live in the same city. Users Bob and Alice are about the same age.")), # 0.6125
        ('Cindy', 'Daisy'): (_count_exp(0.3), 'S-S', (
            "Users Cindy and Daisy live in the same city.",
            "Users Daisy and Cindy live in the same city.")), #0.65
        ('Edgar', 'Fionna'): (_count_exp(1 * 0.2), 'S-S', (
            "Users Edgar and Fionna are about the same age.",
            "Users Fionna and Edgar are about the same age.")),
        
        # O-O
        ('Rubber Shoes', 'Sneakers'): ((_count_exp(0.4) + _count_exp(0.1))/2, 'O-O', (
            "The shoe pairs Rubber Shoes and Sneakers share some keywords. Shoes Sneakers and Rubber Shoes were made by the same manufacturer.",
            "The shoe pairs Rubber Shoes and Sneakers share some keywords. Shoes Rubber Shoes and Sneakers were made by the same manufacturer.",
            "The shoe pairs Sneakers and Rubber Shoes share some keywords. Shoes Sneakers and Rubber Shoes were made by the same manufacturer.",
            "The shoe pairs Sneakers and Rubber Shoes share some keywords. Shoes Rubber Shoes and Sneakers were made by the same manufacturer.")), # 0.625
        ('Sneakers', 'RS 130'): (_count_exp(0.2), 'O-O',(
            "The shoe pairs Sneakers and RS 130 share some keywords.",
            "The shoe pairs RS 130 and Sneakers share some keywords.",)), # 0.6        
    }
    """A dictionary: pair of entities : expectancy, entity_type, description"""

    def test_aggregates_created(self):
        """Test that the aggregates were created as expected"""
        
        # filter aggregated instances for my recommender
        aggr_instances = AggregatedRelationshipInstance.objects.filter(
                            recommender=ShoeRecommender._get_recommender_model())
        
        # assert it has the expected length 
        eq_(aggr_instances.count(), len(self.EXPECTED_AGGREGATES))
        
        for aggr_inst in aggr_instances.iterator():
            pair1 = (aggr_inst.subject_object1.name, aggr_inst.subject_object2.name)
            pair2 = (aggr_inst.subject_object2.name, aggr_inst.subject_object1.name)            
            
            # try getting the instance from expected in both directions
            if self.EXPECTED_AGGREGATES.has_key(pair1):
                expected_expectancy, expected_rel_type, expected_descs = self.EXPECTED_AGGREGATES[pair1]
            else:
                if self.EXPECTED_AGGREGATES.has_key(pair2):
                    expected_expectancy,expected_rel_type, expected_descs = self.EXPECTED_AGGREGATES[pair2]
                else:
                    # if not found it's unexpected.
                    assert False, \
                        "Unexpected aggregate between '%s' and '%s' expectancy: %f" % \
                        (pair1 + (aggr_inst.expectancy, ))

            # assert the expectancy is as expected    
            assert_almost_equal(aggr_inst.expectancy, expected_expectancy, PLACES,
                "Expectancy is '%f' should be '%f' for the pair %s, %s" % \
                    ((aggr_inst.expectancy, expected_expectancy) + pair1)) 
        
            # assert the relationship type is as expected    
            eq_(aggr_inst.relationship_type, expected_rel_type,
                "Relationship type is '%s' should be '%s' for the pair %s, %s" % \
                    ((aggr_inst.relationship_type, expected_rel_type) + pair1)) 
                    
            # assert the description is as expected                    
            assert aggr_inst.description in expected_descs, \
                "Description is '%s' should be one of '%s' for the pair %s, %s" % \
                    ((aggr_inst.description, expected_descs) + pair1) 

    EXP_AGGR_BIASES = {
        'Alice': (_count_exp(0.4 * 0.333333), "User Alice likes many shoe pairs."),
        'Bob': (_count_exp(0.4 * 0.333333), "User Bob likes many shoe pairs."),
        'Edgar': (_count_exp(0.4 * 0.333333), "User Edgar likes many shoe pairs."),
        'Sneakers': (_count_exp(0.8 * 0.6666666), "Shoe pair Sneakers is popular"),
        'Rubber Shoes': (_count_exp(0.8 * 0.333333), "Shoe pair Rubber Shoes is popular"),
    }
    
    def test_aggregated_biases_created(self):
        """Test that the bias aggregates were created as expected"""
        
        # get the aggregates, check count
        #        
        aggregates = AggregatedBiasInstance.objects.all()        
        eq_(aggregates.count(), len(self.EXP_AGGR_BIASES))
        
        # go through created aggregates, assert its in expected and 
        # with expected attrs
        for aggr in aggregates:
               
            assert self.EXP_AGGR_BIASES.has_key(aggr.subject_object.name)
            exp_expectancy, exp_desc = self.EXP_AGGR_BIASES[aggr.subject_object.name]
            
            assert_almost_equal(aggr.expectancy, exp_expectancy, PLACES,
                "Expected expectancy %f, got %f for %s" % \
                (exp_expectancy, aggr.expectancy, aggr.subject_object.name) )
                
            eq_(aggr.description, exp_desc) 
        
                                    

class TestAlgorithm(TestEntities):
    """Testing the building phase of the SimpleAlgorithm"""       
    
    
    EXPECTED_PREDICTIONS = {
        # S-O
        ('Alice', 'RS 130'): _count_neg_exp(0.85), # 0.075
        ('Alice', 'Rubber Shoes'): (_count_exp(0.4) + _count_exp(0.1))/2, # 0.625
        ('Alice', 'Sneakers'): _count_exp(0.1),  # 0.55
        
        ('Bob', 'RS 130'): _count_neg_exp(0.85), # 0.075
        ('Bob', 'Rubber Shoes'): _count_exp(0.1), # 0.55
        ('Bob', 'Sneakers'): (_count_exp(0.4) + _count_exp(0.1))/2, # 0.625

        ('Cindy', 'RS 130'): _count_exp(0.1), # 0.55
        ('Cindy', 'Rubber Shoes'): _count_exp(0.4), # 0.7        
        
        ('Daisy', 'RS 130'): _count_exp(0.1), # 0.55
        
        ('Edgar', 'Sneakers'): (_count_exp(0.1) + _count_exp(0.4))/2, # 0.625 
        
        ('Fionna', 'Rubber Shoes'): _count_exp(0.2),
    }     
    
    def test_predictions_created(self):
        """Test that the predictions were created as expected"""
        
        # filter aggregated instances for my recommender
        pred_instances = RelationshipPredictionInstance.objects.filter(
                            recommender=ShoeRecommender._get_recommender_model())
        
        # assert it has the expected length 
        eq_(pred_instances.count(), len(self.EXPECTED_PREDICTIONS), 
            "expected: %d, obtained: %d, obtained instances: %s" % \
                (len(self.EXPECTED_PREDICTIONS), pred_instances.count(), pred_instances))
        
        for pred_inst in pred_instances.iterator():
            pair1 = (pred_inst.subject_object1.name, pred_inst.subject_object2.name)
            pair2 = (pred_inst.subject_object2.name, pred_inst.subject_object1.name)            
            
            # try getting the instance from expected in both directions
            if self.EXPECTED_PREDICTIONS.has_key(pair1):
                expected_prediction = self.EXPECTED_PREDICTIONS[pair1]
            else:
                if self.EXPECTED_PREDICTIONS.has_key(pair2):
                    expected_prediction = self.EXPECTED_PREDICTIONS[pair2]
                else:
                    # if not found it's unexpected.
                    assert False, \
                        "Unexpected prediction between '%s' and '%s' expectancy: %f" % \
                        (pair1 + (pred_inst.expectancy, ))

            # assert the expectancy is as expected    
            assert_almost_equal(pred_inst.expectancy, expected_prediction, PLACES, 
                "Prediction is '%f' should be '%f' for the pair %s, %s" % \
                    ((pred_inst.expectancy, expected_prediction) + pair1)) 
        

