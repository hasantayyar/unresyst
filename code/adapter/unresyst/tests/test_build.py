"""Tests for the building phase"""

from nose.tools import eq_

from unresyst import Recommender
from unresyst.models.common import SubjectObject, Recommender as RecommenderModel
from test_base import DBTestCase

from demo.recommender import ShoeRecommender
from demo.models import User, ShoePair


class TestRecommender(DBTestCase):
    """Test case for the recommender class"""
    
    def test_recommender_created(self):
        """Test that the recommender was created during the build"""
        
        # build it
        ShoeRecommender.build()
        
        # get it from db
        rec = RecommenderModel.objects.filter(
            class_name=ShoeRecommender.__name__)
        
        # assert there's one            
        eq_(rec.count(), 1, "There should be right one recommender %s." \
            % ShoeRecommender.name)
        
        rec = rec[0]
        
        # assert it has the right name
        eq_(rec.name, ShoeRecommender.name)
        
            
class TestAbstractor(DBTestCase):
    """Testing the abstractor in the build phase"""
    
    def test_create_subjectobjects(self):
        """Test for creating universal subjects, objects"""
        
        # call the tested function
        ShoeRecommender.build()
        
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
