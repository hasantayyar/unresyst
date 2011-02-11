#!/bin/sh

# parametry: 
#  1. co chces evaluovat: lastfm, demo
#  2. cislo iterace


LASTFM=false
DEMO=false

for param in $*;
do    
    case $param in
    'lastfm')
        LASTFM=true
        ;;
    'demo')
        DEMO=true
        ;;
    esac
done

if [ $LASTFM = true ]
then
    echo "Creating test set."
    echo "from lastfm.models import *; ArtistRecommenderValidationPair.select_validation_pairs($2); quit()" | python ./manage.py shell    
    echo "Building and evaluating recommender."
    echo "from lastfm.recommender import *; ArtistRecommender.build(); ArtistRecommender.evaluate(); quit();" | python ./manage.py shell
fi


