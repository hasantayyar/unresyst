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
    echo "from lastfm.recommender import *; ArtistRecommender.ValidationPairClass.select_validation_pairs($2); quit()" | python ./manage.py shell    
    echo "Building and evaluating recommender."
    echo "from lastfm.recommender import *; ArtistRecommender.build(); ArtistRecommender.evaluate(); quit();" | python ./manage.py shell
fi


# select test data
from lastfm.evaluation import *
ArtistRecommenderEvaluator.select_evaluation_pairs()

# evaluate my recommender
#

# build it
from lastfm.recommender import *
ArtistRecommender.build()

# predictions:
#

# evaluate unresyst:
from lastfm.evaluation import *
from lastfm.recommender import *
ArtistRecommenderEvaluator.evaluate_predictions(ArtistRecommender)

# evaluate mahout recommender:
# export training data
from lastfm.mahout_recommender import *
MahoutArtistRecommender.export_data('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_train.csv')

# export test data
from lastfm.evaluation import *
ArtistRecommenderEvaluator.export_evaluation_pairs('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_test.csv')

# run mahout train, test -> lastfm_predictions.csv

# import predictions
from lastfm.mahout_recommender import *
MahoutArtistRecommender.import_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_predictions.csv')

# evaluate the predictions  
from lastfm.mahout_recommender import *
from lastfm.evaluation import *
ArtistRecommenderEvaluator.evaluate_predictions(MahoutArtistRecommender)

# recommendations
# 

# evaluate unresyst
from lastfm.evaluation import *
from lastfm.recommender import *
ArtistRecommenderEvaluator.evaluate_recommendations(ArtistRecommender, 10)

# evaluate mahout recommender

# export training data
from lastfm.mahout_recommender import *
MahoutArtistRecommender.export_data('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_train.csv')


# run mahout train, test -> lastfm_recommendations.csv

# import predictions
from lastfm.mahout_recommender import *
MahoutArtistRecommender.import_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_recommendations.csv')

# evaluate the recommendations  
from lastfm.mahout_recommender import *
from lastfm.evaluation import *
ArtistRecommenderEvaluator.evaluate_recommendations(MahoutArtistRecommender, 10)
