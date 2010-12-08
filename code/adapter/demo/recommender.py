"""The recommender used in the parent system 
(the unresyst.BaseRecommender subclass)
"""

from unresyst import *

from models import *

class ShoeRecommender(Recommender):
    """A BaseRecommender subclass holding all domain-specific data"""
    
    subjects = User.objects
    """The objects to who the recommender will recommend."""
    
    objects = ShoePair.objects
    """The objects that will be recommended.""" 

    predicted_relationship = Relationship( 
        condition=lambda s, o: 
            o in s.shoes.all(), 
        description="""User %(subject)s likes shoes %(object)s."""
    )
    """The relationship that will be predicted"""
    
    relationships = (
        
        # if the user has viewed the shoes it's a sign of preference
        SubjectObjectRelationship(

            condition=lambda s, o:
                o in s.viewed_shoes,
            
            weight=0.4,
            
            description="User %(subject1)s has viewed %(object1)s."
        ),
        
        # if users live in the same city, they are considered similar
        SubjectSimilarityRelationship(
            
            condition=lambda s1, s2:
                s1.home_city == s2.home_city,
                
            weight=0.3,
            
            description="Users %(subject1)s and %(subject2)s live in the same city."
        ),
        
        # if shoes were made by the same manufacturer, they are considered 
        # similar
        ObjectSimilarityRelationship(
            condition=lambda o1, o2:
                o1.manufacturer == o2.manufacturer,
                
            weight=0.1,
            
            description="Shoes %(object1)s and %(object2)s were made by" + \
                " the same manufacturer."
        )     
    )
    """Relationships among the subjects and objects in the domain"""
    
    
    rules = (
        # if user lives on south, don't recommend him winter shoes        
        SubjectObjectRule( 

            # is the user from a southern city?
            condition=lambda s, o: 
                s.home_city.in_south, 

            weight=0.85, 

            # remove from recommendations by returning always 0.
            expectancy=lambda s, o: 0, 
            
            description="%(subject)s is from south, so %(object)s can't " + 
                "be recommended to him/her."
        ),
        
        # if users are the same age +- year they are similar
        SubjectSimilarityRule(
            # both users have given their age
            condition=lambda s1, s2: 
                s1.age and s2.age and s1.age -1 <= s2.age <= s2.age + 1,
            weight=0.2,
            
            # a magic linear expectancy function
            expectancy=lambda s1, s2: 
                1 - 0.25 * abs(s1 - s2),
            
            description="Users %(subject1)s and %(subject2)s are about " + 
                "the same age."
        ),
        
        # if shoes have common keywords, they are similar.
        ObjectSimilarityRule(
            # shoes have some common keywords
            condition=lambda o1, o2: 
                bool(_intersection(o1.keywords, o2.keywords)),          
            
            weight=0.4,
            
            # the size of the intersection / the size of the smaller set
            expectancy=lambda o1, o2: 
                float(len(_intersection(o1.keywords, o2.keywords))) / 
                min(len(o1.keywords), len(o2.keywords)),
            
            description="The shoe pairs %(object1)s and %(object2)s " + 
                "share some keywords."
        ),
    )
    """Rules that can be applied to the domain"""
    
def _intersection(keywords1, keywords2):
    """Intersection of the set of keywords for given by parameters.
    
    @type keywords1: iterable of strings or other type
    @param keywords1: the first list of keywords

    @type keywords2: iterable of strings or other type
    @param keywords2: the second list of keywords    

    @rtype: set of strings (or other type)
    @returns: the intersection
    """
    
    return set([kw.word for kw in keywords1]).intersection( 
                set([kw.word for kw in keywords2]))
