"""The base classes for the tests used in unresyst"""

from django.test import TestCase

from unresyst.models.common import SubjectObject 

from demo.recommender import ShoeRecommender, AverageRecommender
from demo.models import User, ShoePair

class DBTestCase(TestCase):
    """A base class for all tests which need database testing data"""

    def setUp(self):
        """Insert data into the database"""

        # insert test data
        from demo.save_data import save_data
        save_data()
        
    def save_entities(self):
        """Save instances of the entities to the testcase isntance
        to be called in subclasses.
        
        Not distinguishing the recommender."""
        
        self.specific_entities = {
            'Alice': User.objects.get(name="Alice"),
            'Bob': User.objects.get(name="Bob"),
            'Cindy': User.objects.get(name="Cindy"),
            'Daisy': User.objects.get(name="Daisy"),
            'Edgar': User.objects.get(name="Edgar"),
            'Fionna': User.objects.get(name="Fionna"),
            'Sneakers': ShoePair.objects.get(name="Sneakers"),
            "Rubber Shoes": ShoePair.objects.get(name="Rubber Shoes"),
            'RS 130': ShoePair.objects.get(name='RS 130'),
            'Design Shoes': ShoePair.objects.get(name='Design Shoes'),
            'Octane SL': ShoePair.objects.get(name='Design Shoes'),                        
        }
        
        rm = self.recommender._get_recommender_model()
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
            'Daisy': SubjectObject.get_domain_neutral_entity(
                            domain_specific_entity=self.specific_entities['Daisy'], 
                            entity_type='S', 
                            recommender=rm),
            'Edgar': SubjectObject.get_domain_neutral_entity(
                            domain_specific_entity=self.specific_entities['Edgar'], 
                            entity_type='S', 
                            recommender=rm),
            'Fionna': SubjectObject.get_domain_neutral_entity(
                            domain_specific_entity=self.specific_entities['Fionna'], 
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
            'Design Shoes': SubjectObject.get_domain_neutral_entity(
                            domain_specific_entity=self.specific_entities['Design Shoes'], 
                            entity_type='O', 
                            recommender=rm),                            
            'Octane SL': SubjectObject.get_domain_neutral_entity(
                            domain_specific_entity=self.specific_entities['Octane SL'], 
                            entity_type='O', 
                            recommender=rm),                            
        }                         

class TestBuild(DBTestCase):
    """The base class performing build in the setup."""

    def setUp(self):
        """The setup for all tests - build the recommender"""
        super(TestBuild, self).setUp()

        # call the tested function        
        ShoeRecommender.build()

        self.recommender = ShoeRecommender

class TestBuildAverage(DBTestCase):
    """The base class performing AverageRecommender build in the setup"""
    
    def setUp(self):
        """The setup for all tests - build the recommender"""
        super(TestBuildAverage, self).setUp()

        # call the tested function        
        AverageRecommender.build()
        
        self.recommender = AverageRecommender
        
        self.save_entities()
            

class TestEntities(TestBuild):
    """The base class adding universal and specific entitits 
    to the test instance
    """
    
    def setUp(self):
        """Obtain specific and universal subject objects 
        and store them in the test instance
        """ 
        
        super(TestEntities, self).setUp()
        
        self.save_entities()
        

