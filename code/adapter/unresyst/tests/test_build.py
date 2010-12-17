"""Tests for the building phase"""

from nose.tools import eq_

from unresyst import Recommender
from unresyst.models.common import SubjectObject, Recommender as RecommenderModel
from unresyst.models.abstractor import PredictedRelationshipDefinition, \
    RelationshipInstance
from test_base import DBTestCase

from demo.recommender import ShoeRecommender
from demo.models import User, ShoePair

#TODO: otestovat cascade delete na recommenderu

class TestBuild(DBTestCase):
    """The base class for all build tests"""

    def setUp(self):
        """The setup for all tests - build the recommender"""
        super(TestBuild, self).setUp()

        # call the tested function        
        ShoeRecommender.build()


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
        
            
class TestAbstractor(TestBuild):
    """Testing the abstractor in the build phase"""    
    
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
                                
    
    def test_create_predicted_relationship_instances(self):
        """Test creating instances of the predicted relationship."""
        
        # get the relationship definition
        definition = PredictedRelationshipDefinition.remove_subclass_objects().get( \
            recommender=ShoeRecommender.recommender_model)
        
        # get instances of the predicted relationship
        qs = RelationshipInstance.remove_subclass_objects().filter(definition=definition)
        
        # there should be one
        eq_(qs.count(), 1)
            
        instance = qs[0]
        
        # test it has the right properties
        # 
        
        # get alice and sneakers in the universal form
        alice = User.objects.get(name="Alice")
        alice_universal = SubjectObject.get_domain_neutral_entity(
                            domain_specific_entity=alice, 
                            entity_type='S', 
                            recommender=ShoeRecommender.recommender_model)
                            
        sneakers = ShoePair.objects.get(name="Sneakers")
        sneakers_universal = SubjectObject.get_domain_neutral_entity(
                            domain_specific_entity=sneakers, 
                            entity_type='O', 
                            recommender=ShoeRecommender.recommender_model) 

        sneakers = ShoePair.objects.get(name="Sneakers")
        
        # assert everything as expected
        assert instance.contains_object(alice_universal)
        assert instance.contains_object(sneakers_universal)
        eq_(instance.description, "User Alice likes shoes Sneakers.")
