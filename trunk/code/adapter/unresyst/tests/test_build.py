"""Tests for the building phase"""

from nose.tools import eq_
from django.db.models import Q

from unresyst import Recommender
from unresyst.models.common import SubjectObject, Recommender as RecommenderModel
from unresyst.models.abstractor import PredictedRelationshipDefinition, \
    RelationshipInstance, RuleRelationshipDefinition
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
    
    def setUp(self):
        """Obtain specific and universal subject objects 
        and store them in the test instance
        """ 
        
        super(TestAbstractor, self).setUp()
        
        self.specific_entities = {
            'Alice': User.objects.get(name="Alice"),
            'Bob': User.objects.get(name="Bob"),
            'Cindy': User.objects.get(name="Cindy"),
            'Sneakers': ShoePair.objects.get(name="Sneakers"),
            "Rubber Shoes": ShoePair.objects.get(name="Rubber Shoes"),
            'RS 130': ShoePair.objects.get(name='RS 130'),
        }
        
        rm = ShoeRecommender.recommender_model
        self.universal_entities = {
            'Alice': SubjectObject.get_domain_neutral_entity(
                            domain_specific_entity=self.specific_entities['Alice'], 
                            entity_type='S', 
                            recommender=rm),
            'Bob': SubjectObject.get_domain_neutral_entity(
                            domain_specific_entity=self.specific_entities['Bob'], 
                            entity_type='S', 
                            recommender=rm),
            'Cindy': SubjectObject.get_domain_neutral_entity(
                            domain_specific_entity=self.specific_entities['Cindy'], 
                            entity_type='S', 
                            recommender=rm),                            
            'Sneakers': SubjectObject.get_domain_neutral_entity(
                            domain_specific_entity=self.specific_entities['Sneakers'], 
                            entity_type='O', 
                            recommender=rm),
            'Rubber Shoes': SubjectObject.get_domain_neutral_entity(
                            domain_specific_entity=self.specific_entities['Rubber Shoes'], 
                            entity_type='O', 
                            recommender=rm),
            'RS 130': SubjectObject.get_domain_neutral_entity(
                            domain_specific_entity=self.specific_entities['RS 130'], 
                            entity_type='O', 
                            recommender=rm),
        }                            

    
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
        
        # assert everything as expected
        assert instance.contains_object(self.universal_entities['Alice'])
        assert instance.contains_object(self.universal_entities['Sneakers'])
        eq_(instance.description, "User Alice likes shoes Sneakers.")

    def test_create_relationship_definitions(self):
        """Test creating the definitions of the relationships"""
        
        # get definitions related to the shoe recommender
        qs = RuleRelationshipDefinition.objects.filter(
            recommender=ShoeRecommender.recommender_model)
        
        # assert the number of definitions is right
        # TODO + len(ShoeRecommender.rules)
        eq_(qs.count(), len(ShoeRecommender.relationships))
        
        # for each defined type there should be a model definition in db
        for rel in ShoeRecommender.relationships:

            # get the definition model by name (shouldn't throw an error)
            rel_model = qs.get(name=rel.name)
            
            # assert the weight and relationship type are right
            eq_(rel_model.weight, rel.weight)            
            eq_(rel_model.relationship_type, rel.relationship_type)

    
    EXPECTED_RELATIONSHIP_DICT = {
        # relationship name, list of instances - (entity1, entity2, description)
        "User has viewed shoes.": (
            ('Alice', 'Rubber Shoes', "User Alice has viewed Rubber Shoes."),
            ('Bob', 'Sneakers', "User Bob has viewed Sneakers."),
            ('Cindy', 'Rubber Shoes', "User Cindy has viewed Rubber Shoes."),
        ),
        "Users live in the same city.": (
            ('Alice', 'Bob', "Users Alice and Bob live in the same city.",
                "Users Bob and Alice live in the same city."),
        ),
        "Shoes were made by the same manufacturer.": (
            ('Sneakers', 'Rubber Shoes', 
                "Shoes Sneakers and Rubber Shoes were made by the same manufacturer.",
                "Shoes Rubber Shoes and Sneakers were made by the same manufacturer."),
        ),
    }
        
                                
    def test_create_relationship_instances(self):
        """Test creating instances of all the defined relationships."""
        
        # get definitions related to the shoe recommender
        qs = RuleRelationshipDefinition.objects.filter(
            recommender=ShoeRecommender.recommender_model)                
        
        # for each defined type there should be a model definition in db
        for rel in ShoeRecommender.relationships:

            # get the expected data
            expected_relationships = self.EXPECTED_RELATIONSHIP_DICT[rel.name]                        

            # get the definition model by name (shouldn't throw an error)
            definition = qs.get(name=rel.name)
            
            instances = RelationshipInstance.objects.filter(definition=definition)
            
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
                if len(expected_data) == 4:
                    assert instance.description == expected_data[2] or \
                        instance.description == expected_data[3], \
                            "The description '%s' is wrong. Should be '%s' or '%s'" % \
                            (instance.description, expected_data[2], expected_data[3])
                else:
                    eq_(instance.description, expected_data[2])                       
                        
