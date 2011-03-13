"""The recommender used in the parent system 
(the unresyst.BaseRecommender subclass)
"""
from django.db.models import Count

from unresyst import *
from models import *  
from unresyst.algorithm import *
from unresyst.compilator import *
from unresyst.aggregator import *
from unresyst.combinator import *

# helper functions:    
#
    
def _get_keyword_set(o):
    """Get set of keywords for the given shoepair
    """
    return set([kw.word for kw in o.keywords.all()])  

def _keyword_set_similarity(o1, o2):
    """A function measuring similarity of keywords for shoepairs o1 and o2.
    
    Counted as the size of the intersection divided by the size of the 
    smaller set of keywords.
    """
    # make sets of the keywords
    keyword_set1 = _get_keyword_set(o1)
    keyword_set2 = _get_keyword_set(o2)
    
    # the intersection of the keywords
    keyword_intersection = keyword_set1.intersection(keyword_set2)
    
    # size of the smaller set
    min_len = min(len(keyword_set1), len(keyword_set2))
    
    # they have some keywords in common, so min_len is never 0
    
    #the final measure
    return float(len(keyword_intersection))/min_len

def _likes_shoes_generator():
    """A generator for the user likes shoes  relationship"""    
    for u in User.objects.iterator():
        for s in u.likes_shoes.iterator():
            yield (u, s)

def _shoelikers():
    """A generator returning users liking at least one shoepair"""
    for u in User.objects.annotate(num_shoes=Count('likes_shoes')).filter(num_shoes__gte=1):
        yield u


def _popular_shoes():
    """A generator returning shoes that are liked by at least one user"""
    for s in ShoePair.objects.annotate(num_likers=Count('likers')).filter(num_likers__gte=1):
        yield s

def _viewed_shoes_generator():
    """A generator for the user has viewed shoes relationship"""    
    for u in User.objects.iterator():
        for s in u.viewed_shoes.iterator():
            yield (u, s)

def _south_generator():
    """A generator for the rule: if user is from south don't recommend 
    him/her winter shoes.
    """
    for u in User.objects.filter(home_city__in_south=True).iterator():
        for s in ShoePair.objects.filter(for_winter=True).iterator():
            yield (u, s)

# the recommender:
# 

class ShoeRecommender(Recommender):
    """A BaseRecommender subclass holding all domain-specific data"""

    name = "Shoe Recommender"
    """The name"""    
    
    subjects = User.objects
    """The objects to who the recommender will recommend."""
    
    objects = ShoePair.objects
    """The objects that will be recommended.""" 

    predicted_relationship = PredictedRelationship( 
        name="User likes shoes.",
        condition=lambda s, o: 
            o in s.likes_shoes.all(), 
        description="""User %(subject)s likes shoes %(object)s.""",
        generator=_likes_shoes_generator
    )
    """The relationship that will be predicted"""
    
    relationships = (
        
        # if the user has viewed the shoes it's a sign of preference
        SubjectObjectRelationship(
            name="User has viewed shoes.",
            
            condition=lambda s, o:
                o in s.viewed_shoes.all(),  

            is_positive=True, 
                
            weight=0.4,                       
            
            description="User %(subject)s has viewed %(object)s.",
            
            generator=_viewed_shoes_generator
        ),
        
        # if the user is from the same city as the shoe manufacturer, he might like it
        SubjectObjectRelationship(
            name='User lives in the same city as the shoe manufacturer.',
            
            condition=lambda s, o:
                o.manufacturer and s.home_city and o.manufacturer.home_city == s.home_city,

            is_positive=True,            
                
            weight=0.1,           
            
            description="User %(subject)s is from the same city as the manufacturer of %(object)s."
        ),
        
        # if users live in the same city, they are considered similar
        SubjectSimilarityRelationship(
            name="Users live in the same city.",
            
            condition=lambda s1, s2:
                s1.home_city and s1.home_city == s2.home_city, 
                
            is_positive=True,               
            
            weight=0.3,            
            
            description="Users %(subject1)s and %(subject2)s live in the same city."
        ),
        
        # if shoes were made by the same manufacturer, they are considered 
        # similar
        ObjectSimilarityRelationship(
            name="Shoes were made by the same manufacturer.",
            
            condition=lambda o1, o2:
                o1.manufacturer and o1.manufacturer == o2.manufacturer,
                
            is_positive=True,                
            
            weight=0.1,
            
            description="Shoes %(object1)s and %(object2)s were made by" + \
                " the same manufacturer."
        )     
    )
    """Relationships among the subjects and objects in the domain"""
    
    
    rules = (
        # if user lives on south, don't recommend him winter shoes        
        SubjectObjectRule( 
            name="Don't recommend winter shoes for southern users.",
            # is the user from a southern city and shoes for winter?
            condition=lambda s, o: 
                s.home_city.in_south and o.for_winter, 
                
            is_positive=False,
            
            weight=0.85, 
            
            confidence=lambda s, o: 1,             
            
            description="%(subject)s is from south, so %(object)s can't " + 
                "be recommended to him/her.",

            generator=_south_generator
        ),
        
        # if users are the same age +- year they are similar
        SubjectSimilarityRule(
            name="Users with similar age.",
            
            # both users have given their age
            condition=lambda s1, s2: 
                s1.age and s2.age and s1.age -1 <= s2.age <= s2.age + 1,
                
            is_positive=True,   
                
            weight=0.2,
            
            # a magic linear confidence function
            confidence=lambda s1, s2: 
                1 - 0.25 * abs(s1.age - s2.age),
            
            description="Users %(subject1)s and %(subject2)s are about " + 
                "the same age."
        ),
        
        # if shoes have common keywords, they are similar.
        ObjectSimilarityRule(
            name="Shoes with common keywords.",
            
            # shoes have some common keywords, if both empty, it's false
            condition=lambda o1, o2: 
                bool(_get_keyword_set(o1).intersection(_get_keyword_set(o2))),
            
            is_positive=True,
            
            weight=0.4,
            
            # the size of the intersection / the size of the smaller set
            confidence=_keyword_set_similarity,
            
            description="The shoe pairs %(object1)s and %(object2)s " + 
                "share some keywords."
        ),
        
        # explicit rating
        ExplicitSubjectObjectRule(
            name="Shoe rating.",
            
            condition=None,
            
            description="User %(subject)s has rated %(object)s.",
            
            # all pairs user, rated shoes
            generator=lambda: [(r.user, r.shoe_pair) for r in ShoeRating.objects.all()],
            
            # the number of stars divided by five
            expectancy=lambda s, o:float(ShoeRating.objects.get(user=s, shoe_pair=o).stars) / 5,
        ),
    )
    """Rules that can be applied to the domain"""
    
    cluster_sets = (
        # shoe category cluster
        ObjectClusterSet(

            name="Shoe category cluster set.",

            weight=0.3,
            
            filter_entities=ShoePair.objects.filter(category__isnull=False),
            
            get_cluster_confidence_pairs=lambda shoe: ((shoe.category.name, 1),),
            
            description="%(object)s belong to the %(cluster)s category.",
        ),
    )
    
    biases = (
        # people liking many shoepairs are more likely to like some more
        SubjectBias(
            name="Users liking many shoes.",
            
            description="User %(subject)s likes many shoe pairs.",
            
            weight=0.4,           
            
            is_positive=True,
            
            generator=_shoelikers,            
            
            confidence=lambda user: float(user.likes_shoes.count())/3
        ),
        
        # multiply liked shoes are more likely to be liked
        ObjectBias(
            name="Popular shoes",
            
            description="Shoe pair %(object)s is popular",
            
            weight=0.8,
            
            is_positive=True,
            
            generator=_popular_shoes,
            
            confidence=lambda shoe: float(shoe.likers.count())/3
        ),
    )

    random_recommendation_description = "Recommending a random shoe pair to the user."
    
    algorithm = AggregatingAlgorithm(
                inner_algorithm=CompilingAlgorithm(
                    inner_algorithm=SimpleAlgorithm(
                        inner_algorithm=None
                    ),
                    compilator=GetFirstCompilator()
                ),
                aggregator=LinearAggregator()
            )
    """The most basic algorithm is used"""

class AverageRecommender(ShoeRecommender):
    
    name = "Advanced shoe recommender"
    
    algorithm = AggregatingAlgorithm(
                inner_algorithm=CompilingAlgorithm(
                    inner_algorithm=SimpleAlgorithm(
                        inner_algorithm=None
                    ),
                    compilator=CombiningCompilator(combinator=AverageCombinator())
                ),
                aggregator=CombiningAggregator(combinator=AverageCombinator())
            )
    """The normal algorithm is used"""



