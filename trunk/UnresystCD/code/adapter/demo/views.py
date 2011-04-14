"""The views for the demo application"""

from django.http import HttpResponse
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, get_object_or_404


from models import User
from recommender import ShoeRecommender

def view_recommendations(request, user_name):
    """The view for the demo recommendations"""
    
    # get the user and user list from db
    user = get_object_or_404(User, name__iexact=user_name)
    user_list = User.objects.all()
    
    # create user recommendations
    recommendations = ShoeRecommender.get_recommendations(user)
    
    context = {
        'user': user,
        'user_list': user_list,
        'recommendations': recommendations,
        'show_expectancy': True,
    }

    return render_to_response(
        'demo/shoe_recommendations.html',
        dictionary=context, 
        context_instance=RequestContext(request)
    )
    
def view_home_page(request):
    """The view for the demo home page"""

    # get the user list from db
    user_list = User.objects.all()
    
    context = {
        'user_list': user_list,
    }

    return render_to_response(
        'demo/home_page.html',
        dictionary=context, 
        context_instance=RequestContext(request)
    )    
    
  
