"""Tests for combinator, compilator."""
from nose.tools import eq_, assert_almost_equal

from unresyst.models.common import SubjectObject
from unresyst.combinator.base import BaseCombinator
from unresyst.compilator.base import BaseCompilator

from test_base import TestBuildAverage

MIN_COUNT = 5
PLACES = 4

class TestCombinator(TestBuildAverage):
    """Tests for the base combinator"""

    EXPECTED_PROMISING_OBJECTS = {
        'Alice': (('Sneakers', 'Design Shoes'), ('Rubber Shoes', 'Sneakers', 'Rubber Shoes', 'Design Shoes'), ('Rubber Shoes', 'RS 130', 'Sneakers'), ('Sneakers', 'Rubber Shoes')),
        'Bob': (('Sneakers', 'Design Shoes'), ('Sneakers', 'Sneakers', 'Rubber Shoes'), ('Rubber Shoes', 'RS 130', 'Sneakers'), ('Sneakers', 'Rubber Shoes')),
        'Cindy': ((), ('Rubber Shoes', 'RS 130'), (), ('Sneakers', 'Rubber Shoes')),
        'Daisy': ((), ('RS 130',), (), ('Sneakers', 'Rubber Shoes')),
        'Edgar': ((), (), ('Sneakers',), ('Sneakers', 'Rubber Shoes'), ('RS 130', 'Octane SL')),
        'Fionna': ((), (), ('Rubber Shoes',), ('Sneakers', 'Rubber Shoes'), ('RS 130',)),
    }
    """Dictionary subject: tuple( tuple from clusters, tuple from s-o rules, tuple from similarities, tuple from biases)
    """

    def dtest_choose_promising_objects(self):
        """Test choosing promising objects for subjects"""

        r = self.recommender._get_recommender_model()
        bc = BaseCombinator()

        for subj in SubjectObject.objects.filter(recommender=r, entity_type='S'):

            # choose it
            promobjs = bc.choose_promising_objects(dn_subject=subj, min_count=MIN_COUNT)
            
            # compare it
            eq_((subj, set(promobjs)), (subj, set([self.universal_entities[oname] for tup in self.EXPECTED_PROMISING_OBJECTS[subj.name] for oname in tup])))
            
class TestCompilator(TestBuildAverage):
    """Tests for the base compilator"""
    EXPECTED_COMBINATION_ELEMENTS = {
                
        ('Alice', 'Sneakers'): (
            [(0.566667, 'User Alice likes many shoe pairs.'), (0.766667, 'Shoe pair Sneakers is popular')], 
            [(0.550000, 'User Alice is from the same city as the manufacturer of Sneakers.')], 
            [],
            [(0.612500, 'Similarity: Reason 1: Users Alice and Bob live in the same city. Reason 2: Users Alice and Bob are about the same age. And: User Bob likes shoes Sneakers.')],
            [],
            [],
        ),
                        
        ('Alice', 'Rubber Shoes'): (
            [(0.566667, 'User Alice likes many shoe pairs.'), (0.633333, 'Shoe pair Rubber Shoes is popular')], 
            [(0.700000, 'User Alice has viewed Rubber Shoes.'), (0.550000, 'User Alice is from the same city as the manufacturer of Rubber Shoes.')], 
            [(0.625000, 'User Alice likes shoes Sneakers. And similarity: Reason 1: The shoe pairs Sneakers and Rubber Shoes share some keywords. Reason 2: Shoes Sneakers and Rubber Shoes were made by the same manufacturer.')],
            [],
            [],
            [],
        ),            
                        
        ('Alice', 'RS 130'): (
            [(0.566667, 'User Alice likes many shoe pairs.'), (0.633333, 'Shoe pair RS 130 is popular')], 
            [(0.075000, "Alice is from south, so RS 130 can't be recommended to him/her.")],
            [],
            [],
            [],
            [],
        ),
            
        ('Alice', 'Design Shoes'): (
            [(0.566667, 'User Alice likes many shoe pairs.')], 
            [],
            [(0.625000, 'User Alice likes shoes Sneakers. And similarity: Reason 1: Sneakers belong to the Casual category. Design Shoes belong to the Casual category. Reason 2: The shoe pairs Sneakers and Design Shoes share some keywords.')],
            [],
            [],
            [],
        ),
                    
        ('Alice', 'Octane SL'): (
            [(0.566667, 'User Alice likes many shoe pairs.')], 
            [],
            [],
            [],
            [],
            [],
        ),
                    
        ('Bob', 'Sneakers'): (
            [(0.566667, 'User Bob likes many shoe pairs.'), (0.766667, 'Shoe pair Sneakers is popular')], 
            [(0.700000, 'User Bob has viewed Sneakers.'), (0.550000, 'User Bob is from the same city as the manufacturer of Sneakers.')], 
            [],
            [(0.612500, 'Similarity: Reason 1: Users Alice and Bob live in the same city. Reason 2: Users Alice and Bob are about the same age. And: User Alice likes shoes Sneakers.')],
            [],
            [],
        ),            
            
        ('Bob', 'Rubber Shoes'): (
            [(0.566667, 'User Bob likes many shoe pairs.'), (0.633333, 'Shoe pair Rubber Shoes is popular')], 
            [(0.550000, 'User Bob is from the same city as the manufacturer of Rubber Shoes.')], 
            [(0.625000, 'User Bob likes shoes Sneakers. And similarity: Reason 1: The shoe pairs Sneakers and Rubber Shoes share some keywords. Reason 2: Shoes Sneakers and Rubber Shoes were made by the same manufacturer.')], 
            [],
            [],            
            [],
        ),
                    
        ('Bob', 'RS 130'): (
            [(0.566667, 'User Bob likes many shoe pairs.'), (0.633333, 'Shoe pair RS 130 is popular')], 
            [(0.075000, "Bob is from south, so RS 130 can't be recommended to him/her.")], 
            [],
            [],
            [],
            [],
        ),
                    
        ('Bob', 'Design Shoes'): (
            [(0.566667, 'User Bob likes many shoe pairs.')], 
            [],
            [(0.625000, 'User Bob likes shoes Sneakers. And similarity: Reason 1: Sneakers belong to the Casual category. Design Shoes belong to the Casual category. Reason 2: The shoe pairs Sneakers and Design Shoes share some keywords.')],
            [],
            [],
            [],
        ),
                    
        ('Bob', 'Octane SL'): (
            [(0.566667, 'User Bob likes many shoe pairs.')], 
            [],
            [],
            [],
            [],
            [],
        ),
                    
        ('Cindy', 'Sneakers'): (
            [(0.766667, 'Shoe pair Sneakers is popular')], 
            [],
            [],
            [],
            [],
            [(0.550000, 'Similarity: Cindy has searched for the word Comfortable. Bob has searched for the word Comfortable. And: User Bob likes shoes Sneakers.')],
        ),

            
        ('Cindy', 'Rubber Shoes'): (
            [(0.633333, 'Shoe pair Rubber Shoes is popular')], 
            [(0.700000, 'User Cindy has viewed Rubber Shoes.')],
            [],
            [],
            [],
            [],
        ),
                    
        ('Cindy', 'RS 130'): (
            [(0.633333, 'Shoe pair RS 130 is popular')], 
            [(0.550000, 'User Cindy is from the same city as the manufacturer of RS 130.')],
            [],
            [],
            [],
            [],
        ),
                    
        ('Cindy', 'Design Shoes'): (
            [], 
            [],
            [],
            [],
            [],
            [],
        ),
                    
        ('Cindy', 'Octane SL'): (
            [], 
            [],
            [],
            [],
            [],
            [],
        ),
                    
        ('Daisy', 'Sneakers'): (
            [(0.766667, 'Shoe pair Sneakers is popular')], 
            [],
            [],
            [],
            [],
            [],
        ),
                    
        ('Daisy', 'Rubber Shoes'): (
            [(0.633333, 'Shoe pair Rubber Shoes is popular')], 
            [],
            [],
            [],
            [],
            [],
        ),
                    
        ('Daisy', 'RS 130'): (
            [(0.633333, 'Shoe pair RS 130 is popular')], 
            [(0.550000, 'User Daisy is from the same city as the manufacturer of RS 130.')],
            [],
            [],
            [],
            [],
        ),            
            
        ('Daisy', 'Design Shoes'): (
            [], 
            [],
            [],
            [],
            [],
            [],
        ),
                    
        ('Daisy', 'Octane SL'): (
            [], 
            [],
            [],
            [],
            [],
            [],
        ),
                    
        ('Edgar', 'Sneakers'): (
            [(0.633333, 'User Edgar likes many shoe pairs.'), (0.766667, 'Shoe pair Sneakers is popular')],
            [],
            [(0.625000, 'User Edgar likes shoes Rubber Shoes. And similarity: Reason 1: The shoe pairs Sneakers and Rubber Shoes share some keywords. Reason 2: Shoes Sneakers and Rubber Shoes were made by the same manufacturer.')],
            [],
            [],
            [],
        ),
                    
        ('Edgar', 'Rubber Shoes'): (
            [(0.633333, 'User Edgar likes many shoe pairs.'), (0.633333, 'Shoe pair Rubber Shoes is popular')], 
            [],
            [],
            [],
            [],
            [],
        ),
                    
        ('Edgar', 'RS 130'): (
            [(0.633333, 'User Edgar likes many shoe pairs.'), (0.633333, 'Shoe pair RS 130 is popular')], 
            [],
            [],
            [],
            [],
            [],
        ),
                    
        ('Edgar', 'Design Shoes'): (
            [(0.633333, 'User Edgar likes many shoe pairs.')], 
            [],
            [],
            [],
            [],
            [],
        ),
                    
        ('Edgar', 'Octane SL'): (
            [(0.633333, 'User Edgar likes many shoe pairs.')], 
            [],
            [],
            [],
            [(0.650000, 'User Edgar likes shoes RS 130. And similarity: RS 130 belong to the For Sports category. Octane SL belong to the For Sports category.')],
            [],
        ),
            
        ('Fionna', 'Sneakers'): (
            [(0.766667, 'Shoe pair Sneakers is popular')], 
            [],
            [],
            [],
            [],
            [],
        ),
                    
        ('Fionna', 'Rubber Shoes'): (
            [(0.633333, 'Shoe pair Rubber Shoes is popular')], 
            [],
            [],
            [(0.600000, 'Similarity: Users Edgar and Fionna are about the same age. And: User Edgar likes shoes Rubber Shoes.')],
            [],
            [],
        ),            
        
        ('Fionna', 'RS 130'): (
            [(0.633333, 'Shoe pair RS 130 is popular')], 
            [],
            [],
            [(0.600000, 'Similarity: Users Edgar and Fionna are about the same age. And: User Edgar likes shoes RS 130.')],
            [],
            [],
        ),
                    
        ('Fionna', 'Design Shoes'): (
            [], 
            [],
            [],
            [],
            [],
            [],
        ),
                    
        ('Fionna', 'Octane SL'): (
            [], 
            [],
            [],
            [],
            [],
            [],
        ),            
    }
    """Dictionary s-o pair: tuple of elements 
        (the pair: expectancy, description): 
         - bias, 
         - s-o relationships
         - predicted + object similarity
         - predicted + subject similarity
         - predicted + object cluster
         - predicted + subject cluster
    """
    

    
    def dtest_get_pair_combination_elements(self):
        """Test getting all we know for the given s-o pairs"""

        r = self.recommender._get_recommender_model()
                
        bc = BaseCompilator()

        # for all subject - object pairs
        for subj in SubjectObject.objects.filter(recommender=r, entity_type='S'):

            for obj in SubjectObject.objects.filter(recommender=r, entity_type='O'):
            
                dn_subject = self.universal_entities[subj.name]
                dn_object = self.universal_entities[obj.name]
                
                # call the tested function            
                els = bc.get_pair_combination_elements(dn_subject, dn_object)
                
                expected_data = self.EXPECTED_COMBINATION_ELEMENTS[(subj.name, obj.name)]
                
                # flatten the expected data
                flat_data = [pair for listt in expected_data for pair in listt]

                # assert the length is right                
                eq_(len(flat_data), len(els), "Expected: %d, Obtained %d. For pair %s, %s  Obtained data: %s" % \
                    (len(flat_data), len(els), subj, obj, els))
                                
                for el in els:
                    
                    # try finding the description in the expected data
                    found = filter(lambda pair: pair[1]==el.get_description(), flat_data)
                    
                    eq_(len(found), 1, "The description %s wasn't found for the pair %s, %s" % (el.get_description(), subj, obj))
                    found = found[0]
                    
                    assert_almost_equal(found[0], el.get_expectancy(), PLACES,
                        "The expectancy is wrong for pair %s, %s. Expected %f, Got %f" % (subj, obj, found[0], el.get_expectancy()))
                
