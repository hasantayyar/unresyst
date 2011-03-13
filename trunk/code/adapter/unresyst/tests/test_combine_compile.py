"""Tests for combinator, compilator."""
from nose.tools import eq_

from unresyst.models.common import SubjectObject
from unresyst.combinator.base import BaseCombinator

from test_base import TestBuildAverage

MIN_COUNT = 5

class TestCombinator(TestBuildAverage):
    """Tests for the base combinator"""

    EXPECTED_PROMISING_OBJECTS = {
        'Alice': (('Sneakers', 'Design Shoes'), ('Rubber Shoes', 'Sneakers', 'Rubber Shoes', 'Design Shoes'), ('Rubber Shoes', 'RS 130', 'Sneakers'), ('Sneakers', 'Rubber Shoes')),
        'Bob': (('Sneakers', 'Design Shoes'), ('Sneakers', 'Sneakers', 'Rubber Shoes'), ('Rubber Shoes', 'RS 130', 'Sneakers'), ('Sneakers', 'Rubber Shoes')),
        'Cindy': ((), ('Rubber Shoes', 'RS 130'), (), ('Sneakers', 'Rubber Shoes')),
        'Daisy': ((), ('RS 130',), (), ('Sneakers', 'Rubber Shoes')),
        'Edgar': ((), (), ('Sneakers',), ('Sneakers', 'Rubber Shoes')),
        'Fionna': ((), (), ('Rubber Shoes',), ('Sneakers', 'Rubber Shoes')),
    }
    """Dictionary subject: tuple( tuple from clusters, tuple from s-o rules, tuple from similarities, tuple from biases)
    """

    def test_choose_promising_objects(self):
        """Test choosing promising objects for subjects"""

        r = self.recommender._get_recommender_model()
        bc = BaseCombinator()

        for s in SubjectObject.objects.filter(recommender=r, entity_type='S'):

            # choose it
            promobjs = bc.choose_promising_objects(dn_subject=s, min_count=MIN_COUNT)
            
            # compare it
            eq_(set(promobjs), set([self.universal_entities[name] for tup in self.EXPECTED_PROMISING_OBJECTS[s.name] for name in tup]))
            
class TestCompilator(TestBuildAverage):
    """Tests for the base compilator"""
    EXPECTED_COMBINATION_ELEMENTS = {
        ('Alice', 'Sneakers'): ((
    }
    """Dictionary s-o pair: tuple of elements (the pair: expectancy, description)"""
    
    def test_get_pair_combination_elements(self):
        """Test getting all we know for the given s-o pairs"""
        
        
                
