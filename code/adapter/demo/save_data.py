"""Saving some data to the demo application"""

from demo.models import *

def save_data():
    """Save test data for the demo application"""
    
    # keywords
    comfortable = Keyword(word="Comfortable")
    comfortable.save()
    
    trainers = Keyword(word="Trainers")
    trainers.save()
    
    sporty = Keyword(word="Sporty")
    sporty.save()
    
    cool = Keyword(word='Cool')
    cool.save()

    # cities
    hollywood = City(name="Hollywood", in_south=True)
    hollywood.save()
    
    helsinki = City(name="Helsinki", in_south=False)        
    helsinki.save()
    
    # manufacturers    
    diesel = Manufacturer(name="Diesel", home_city=hollywood)
    diesel.save()
    
    lange = Manufacturer(name="Lange", home_city=helsinki)
    lange.save()
    
    # shoes
    sneakers = ShoePair(
        name="Sneakers",
        manufacturer=diesel,
        for_winter=False,
        image_path='/images/Trainers.gif'
    )
    sneakers.save()
    sneakers.keywords.add(comfortable,trainers, cool)
    sneakers.save()
    
    rubber_shoes = ShoePair(
        name="Rubber Shoes",
        manufacturer=diesel,
        for_winter=False,
        image_path='/images/Rubber_Boots.gif'
    )
    rubber_shoes.save()
    rubber_shoes.keywords.add(comfortable)
    rubber_shoes.save()
    
    ski_boots = ShoePair(
        name='RS 130',
        manufacturer=lange,
        for_winter=True,
        image_path='/images/ski-boot.jpg'        
    )
    ski_boots.save()
    ski_boots.keywords.add(sporty, cool)
    ski_boots.save()
    
    # users    
    alice = User(
        name="Alice",
        age=19,
        home_city=hollywood
    )
    alice.save()
    alice.viewed_shoes.add(rubber_shoes)
    alice.likes_shoes.add(sneakers)
    alice.words_searched.add(trainers)
    alice.save()
    
    bob = User(
        name="Bob",
        age=18,
        home_city=hollywood
    )
    bob.save()
    bob.viewed_shoes.add(sneakers)
    bob.words_searched.add(sporty, comfortable)
    bob.likes_shoes.add(sneakers)
    bob.save()
    
    cindy = User(
        name="Cindy",
        age=25,
        home_city=helsinki
    )
    cindy.save()
    cindy.viewed_shoes.add(rubber_shoes)
    cindy.save()
    
    daisy = User(
        name="Daisy",
        age=32,
        home_city=helsinki
    )
    daisy.save()
    
                    
