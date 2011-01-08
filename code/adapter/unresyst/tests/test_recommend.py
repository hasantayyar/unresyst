"""Tests for the recommend phase.

The test are always started by running the recommender.build method.
"""


from nose.tools import eq_, assert_raises, assert_almost_equal

from test_base import TestBuild, TestEntities
from demo.recommender import ShoeRecommender
from demo.models import User, ShoePair

from unresyst.exceptions import InvalidParameterError

def _count_exp(conf):
    return 0.5 + conf/2
    
def _count_neg_exp(conf):    
    return 0.5 - conf/2

EXPECTED_PREDICTIONS = {
    # S-O
    ('Alice', 'RS 130'): (_count_neg_exp(0.85), "Alice is from south, so RS 130 can't be recommended to him/her."), # 0.075
    ('Alice', 'Rubber Shoes'): ((_count_exp(0.4) + _count_exp(0.1))/2, 
        'User Alice has viewed Rubber Shoes. User Alice is from the same city as manufacturer of Rubber Shoes.'),# 0.625
    ('Alice', 'Sneakers'): (0, "User Alice likes shoes Sneakers."), 
    
    ('Bob', 'RS 130'): (_count_neg_exp(0.85), "Bob is from south, so RS 130 can't be recommended to him/her."), # 0.075
    ('Bob', 'Rubber Shoes'): (_count_exp(0.1), "User Bob is from the same city as manufacturer of Rubber Shoes."), # 0.55
    ('Bob', 'Sneakers'): (0, "User Bob likes shoes Sneakers."),

    ('Cindy', 'RS 130'): (_count_exp(0.1), "User Cindy is from the same city as manufacturer of RS 130."), # 0.55
    ('Cindy', 'Rubber Shoes'): (_count_exp(0.4), "User Cindy has viewed Rubber Shoes."), # 0.7        
    ('Cindy', 'Sneakers'): (0.5, ''), 
    
    ('Daisy', 'RS 130'): (_count_exp(0.1), "User Daisy is from the same city as manufacturer of RS 130."), # 0.55
    ('Daisy', 'Rubber Shoes'): (0.5, ''), 
    ('Daisy', 'Sneakers'): (0.5, ''),         
}   
"""A dictionary: name: (prediction, explanation)"""



class TestPredictRelationship(TestEntities):
    """Testing the predict_relationship function"""    
        
    def test_predictions(self):
        """Test predictions are made as expected"""

        # go through all predictions to expect
        for k, v in EXPECTED_PREDICTIONS.items():
            subj = self.specific_entities[k[0]]
            obj = self.specific_entities[k[1]]
            
            # get prediction for the pair
            pred = ShoeRecommender.predict_relationship(subj, obj)
            
            # assert expectancy is right
            eq_(v[0], pred.expectancy)

            # assert explanation is right
            eq_(v[1], pred.explanation)

    def test_non_existing_subject(self):
        """Test raising the right error when passing non-existing subject"""
        
        # create and save unknown user
        unknown = User(
            name="Anonymous",
            age=10
        )
        unknown.save()
        
        obj = self.specific_entities['Rubber Shoes']
        
        # assert it throws an error
        assert_raises(InvalidParameterError, ShoeRecommender.predict_relationship, unknown, obj)
        
        
    def test_non_existing_subject(self):
        """Test raising the right error when passing non-existing object"""

        subj = self.specific_entities['Alice']
        
        # create and save unknown shoepair
        unknown =  ShoePair(
            name="XYZ",    
        )        
        unknown.save()        
        
        # assert the method throws an error.
        assert_raises(InvalidParameterError, ShoeRecommender.predict_relationship, subj, unknown)

_EXPECTED_RECOMMENDATIONS = dict(
    [(name, 
        filter(lambda (shoes, expe, expl): expe > 0, 
            sorted(
                [(shoes, expe, expl) for (n, shoes), (expe, expl) in 
                    filter(lambda ((n, x),(xx, xxx)): n==name, EXPECTED_PREDICTIONS.items())
                ], 
        key=lambda tup: tup[1], reverse=True)), 
    ) for (name, xx)  in EXPECTED_PREDICTIONS.keys()]
)
"""A dictionary name: list of (shoes, expectancy, explanation) sorted by 
expectancy in reverse order, the zero expectancy recommendations are removed.
"""

EXPECTED_RECOMMENDATIONS = {
    'Bob': [
        ('Rubber Shoes', 0.55, 'User Bob is from the same city as manufacturer of Rubber Shoes.'),
        ('RS 130', 0.075000000000000011, "Bob is from south, so RS 130 can't be recommended to him/her.")
    ], 
    'Alice': [
        ('Rubber Shoes', 0.625, 'User Alice has viewed Rubber Shoes. User Alice is from the same city as manufacturer of Rubber Shoes.'), 
        ('RS 130', 0.075, "Alice is from south, so RS 130 can't be recommended to him/her.")
    ], 
    'Cindy': [
        ('Rubber Shoes', 0.7, 'User Cindy has viewed Rubber Shoes.'), 
        ('RS 130', 0.55, 'User Cindy is from the same city as manufacturer of RS 130.'), 
        ('Sneakers', 0.5, '')
    ], 
    'Daisy': [
        ('RS 130', 0.55, 'User Daisy is from the same city as manufacturer of RS 130.'), 
        ('Sneakers', 0.5, ''), 
        ('Rubber Shoes', 0.5, '')
    ]
}
"""The same but a bit more explicit"""


EXPECTED_RECOMMENDATIONS_COUNT = {
    'Bob': [
        ('Rubber Shoes', 0.55, 'User Bob is from the same city as manufacturer of Rubber Shoes.'),
        ('RS 130', 0.075, "Bob is from south, so RS 130 can't be recommended to him/her.")
    ], 
    'Alice': [
        ('Rubber Shoes', 0.625, 'User Alice has viewed Rubber Shoes. User Alice is from the same city as manufacturer of Rubber Shoes.'), 
        ('RS 130', 0.075, "Alice is from south, so RS 130 can't be recommended to him/her.")
    ], 
    'Cindy': [
        ('Rubber Shoes', 0.7, 'User Cindy has viewed Rubber Shoes.'), 
        ('RS 130', 0.55, 'User Cindy is from the same city as manufacturer of RS 130.'), 
    ], 
    'Daisy': [
        ('RS 130', 0.55, 'User Daisy is from the same city as manufacturer of RS 130.'), 
        ('Sneakers', 0.5, ''), 
    ]
}
"""Recommendations when the count is 2"""

EXPECTED_RECOMMENDATIONS_LIMIT = {
    'Bob': [
        ('Rubber Shoes', 0.55, 'User Bob is from the same city as manufacturer of Rubber Shoes.'),
    ], 
    'Alice': [
        ('Rubber Shoes', 0.625, 'User Alice has viewed Rubber Shoes. User Alice is from the same city as manufacturer of Rubber Shoes.'), 
    ], 
    'Cindy': [
        ('Rubber Shoes', 0.7, 'User Cindy has viewed Rubber Shoes.'), 
        ('RS 130', 0.55, 'User Cindy is from the same city as manufacturer of RS 130.'), 
    ], 
    'Daisy': [
        ('RS 130', 0.55, 'User Daisy is from the same city as manufacturer of RS 130.'), 
    ]
}
"""Recommndations when the expectancy limit is 0.5"""

class TestGetRecommendations(TestEntities):
    """Test the get_recommendations function"""
    
    def test_recommendations(self):
        """Test recommendations are made as expected"""
        self._test_recs(EXPECTED_RECOMMENDATIONS)

    def test_recommendations_with_count(self):
        """Test recommendations when setting count"""
        self._test_recs(EXPECTED_RECOMMENDATIONS_COUNT, 2)
        
    def test_recommendations_with_limit(self):
        """Test recommendations when setting the expectancy limit"""
        
        #change the expectancy limit
        lim = ShoeRecommender.recommendation_expectancy_limit
        ShoeRecommender.recommendation_expectancy_limit = 0.5
        
        self._test_recs(EXPECTED_RECOMMENDATIONS_LIMIT)
        
        # restore it
        ShoeRecommender.recommendation_expectancy_limit = lim

    def _test_recs(self, expected_dict, count=None):
    
        # go through all expected recommendations
        for name, exp_rec_list in expected_dict.items():
            
            subj = self.specific_entities[name]
                        
            # get recommendations for the subject
            rec_list = ShoeRecommender.get_recommendations(subj) \
                if count is None else ShoeRecommender.get_recommendations(subj,count)
            
            # assert the count is as expected
            eq_(len(rec_list), len(exp_rec_list))
            
            # assert all recommendation items are as expected
            for (exp_shoe_name, exp_expe, exp_expl), pred in zip(exp_rec_list, rec_list):

                # assert the recommended object is right
                eq_(self.specific_entities[exp_shoe_name], pred.object_)
                
                # assert expectancy is right
                assert_almost_equal(exp_expe, pred.expectancy, 4)

                # assert explanation is right
                eq_(exp_expl, pred.explanation)                           
        

    def test_non_existing_subject(self):
        """Test raising the right error when passing non-existing subject - recommendations"""
        
        # create and save unknown user
        unknown = User(
            name="Anonymous",
            age=10
        )
        unknown.save()        
        
        # assert it throws an error
        assert_raises(InvalidParameterError, ShoeRecommender.get_recommendations, unknown)    
    