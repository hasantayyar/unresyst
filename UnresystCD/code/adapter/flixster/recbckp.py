    relationships = (
        # users in friendship
        SubjectSimilarityRelationship(
            name="Users are friends.",
            
            generator=lambda: [(f.friend1, f.friend2) for f in Friend.objects.all()], 
            
            is_positive=True,               
            
            weight=0.5,            
            
            description="Users %(subject1)s and %(subject2)s are friends.",
        ),
    )
    """The relationships"""
    
    biases = (
        # people giving high ratings
        SubjectBias(
            name="Users giving high ratings.",
            
            description="User %(subject)s gives high ratings.",
            
            weight=0.5,           
            
            is_positive=True,
            
            generator=lambda: User.objects.annotate(avg_rating=Avg('rating__rating')).filter(avg_rating__gt=str(MIN_HIGH_RATING)),            
            
            confidence=lambda user: user.rating_set.aggregate(Avg('rating'))['rating__avg'] - MIN_HIGH_RATING
        ),
        
        # highly rated movies
        ObjectBias(
            name="High-rated movies.",
            
            description="Movie %(object)s is high-rated",
            
            weight=0.5,
            
            is_positive=True,
            
            generator=lambda: Movie.objects.annotate(avg_rating=Avg('rating__rating')).filter(avg_rating__gt=str(MIN_HIGH_RATING)),
            
            confidence=lambda movie: movie.rating_set.aggregate(Avg('rating'))['rating__avg'] - MIN_HIGH_RATING
        ),
        
        # people giving low ratings
        SubjectBias(
            name="Users giving low ratings.",
            
            description="User %(subject)s gives low ratings.",
            
            weight=0.5,           
            
            is_positive=False,
            
            generator=lambda: User.objects.annotate(avg_rating=Avg('rating__rating')).filter(avg_rating__lt=str(MAX_LOW_RATING)),            
            
            confidence=lambda user: MAX_LOW_RATING - user.rating_set.aggregate(Avg('rating'))['rating__avg'] 
        ),
        
        # low-rated movies
        ObjectBias(
            name="Low-rated movies.",
            
            description="Movie %(object)s is low-rated",
            
            weight=0.5,
            
            is_positive=False,
            
            generator=lambda: Movie.objects.annotate(avg_rating=Avg('rating__rating')).filter(avg_rating__lt=str(MAX_LOW_RATING)),
            
            confidence=lambda movie: MAX_LOW_RATING - movie.rating_set.aggregate(Avg('rating'))['rating__avg']
        ),        
    )
    
