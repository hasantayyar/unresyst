    rules = (          
        # click = sign of preference
        SubjectObjectRule(
            name='User has clicked on something on the tour profile.',
            weight=0.5,
            condition=None,
            is_positive=True,
            description='User %(subject)s has clicked on something on the %(object)s profile.',
            # pairs that user has clicked on the tour
            generator=lambda: ((User.objects.get(pk=uid), Tour.objects.get(pk=tid)) \
                for uid, tid in Click.objects.values_list('session__user', 'tour').distinct()),
            # the average is around 3, so take 1/6. so that 3 points to the middle.
            confidence=lambda u, t: min(float(Click.objects.filter(tour=t, session__user=u).count())/6, 1.0),
        ),
        
        # question .. also a sign of preference
        SubjectObjectRule(
            name='User has asked about the tour.',
            weight=0.5,
            condition=None,
            is_positive=True,
            description='User %(subject)s has asked about %(object)s.',
            # pairs that user has asked on the tour
            generator=lambda: ((User.objects.get(pk=uid), Tour.objects.get(pk=tid)) \
                for uid, tid in Question.objects.values_list('session__user', 'tour').distinct()),
            confidence=lambda u, t: min(float(Question.objects.filter(tour=t, session__user=u).count())/2, 1.0),
        ),
        
        # mouse move .. also a sign of preference
        SubjectObjectRule(
            name='User has moved the mouse on the tour profile.',
            weight=0.5,
            condition=None,
            is_positive=True,
            description='User %(subject)s has moved the mouse on %(object)s.',
            # pairs that user has moved on the tour
            generator=lambda: ((User.objects.get(pk=uid), Tour.objects.get(pk=tid)) \
                for uid, tid in MouseMove.objects.values_list('session__user', 'tour').distinct()),
            confidence=lambda u, t: min(float(MouseMove.objects.filter(tour=t, session__user=u).count())/18, 1.0),
        ),
        
        # view profile 
        SubjectObjectRule(
            name='User has viewed the tour profile page.',
            weight=0.5,
            condition=None,
            is_positive=True,
            description='User %(subject)s has viewed %(object)s.',
            # pairs that user has viewed the tour
            generator=lambda: ((User.objects.get(pk=uid), Tour.objects.get(pk=tid)) \
                for uid, tid in ViewProfile.objects.values_list('session__user', 'tour').distinct()),
            # how many times * how long
            confidence=_viewed_profile_confidence
        ),

       
    )
    
    cluster_sets = (
        # cluster - tour types
        ObjectClusterSet(

            name="Tour type cluster set.",

            weight=0.5,
            
            filter_entities=Tour.objects.all(),
            
            get_cluster_confidence_pairs=lambda tour: ((tour.tour_type.name, 1),),
            
            description="The tour %(object)s has type %(cluster)s.",
        ),
        
        # cluster - countries
        ObjectClusterSet(

            name="Country cluster set.",

            weight=0.5,
            
            filter_entities=Tour.objects.all(),
            
            get_cluster_confidence_pairs=lambda tour: ((tour.country.name, 1),),
            
            description="The tour %(object)s is to %(cluster)s country.",
        ),

    )
    
    biases = (
        # multiply viewed tours
        ObjectBias(
            name="Most viewed tours.",
            
            description="Tour %(object)s is much viewed",
            
            weight=0.5,
            
            is_positive=True,
            
            generator=lambda: Tour.objects.annotate(hh=Count('viewprofile')).filter(hh__gt=2).distinct(),
            
            confidence=lambda t: min(float(t.viewprofile_set.count())/4, 1.0)
        ),
        
        # multiply clicked tours
        ObjectBias(
            name="Most clicked tours.",
            
            description="Tour %(object)s is often clicked on.",
            
            weight=0.5,
            
            is_positive=True,
            
            generator=lambda: Tour.objects.annotate(hh=Count('click')).filter(hh__gt=1).distinct(),
            
            confidence=lambda t: min(float(t.click_set.count())/2, 1.0)
        ),
        
        # multiply mouse moved tours
        ObjectBias(
            name="Most mouse moved tours.",
            
            description="Tour %(object)s is often mouse moved.",
            
            weight=0.5,
            
            is_positive=True,
            
            generator=lambda: Tour.objects.annotate(hh=Count('mousemove')).filter(hh__gt=6).distinct(),
            
            confidence=lambda t: min(float(t.mousemove_set.count())/12, 1.0)
        ),
    )



    

