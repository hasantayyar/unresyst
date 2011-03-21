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

# LASTFM
#
#

# specificky pro lastfm - dva test sety
from lastfm.models import *
BaseArtistEvaluationPair.select()

# select test data - obecne
from lastfm.evaluation import *
MovieRecommenderEvaluator.select_evaluation_pairs()

# evaluate my recommender
#

# build it
from lastfm.recommender import *
ArtistRecommender.build()

# predictions:
#

# evaluate unresyst (predictions):
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
cd ../mahout/mahoutrec
./unresystpredict.sh lastfm

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
# nenovel:

# export training data
from lastfm.mahout_recommender import *
MahoutArtistRecommender.export_data('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_train.csv')

# run mahout train, test -> lastfm_recommendations.csv
cd ../mahout/mahoutrec
./unresystrecommend.sh

# import predictions
from lastfm.mahout_recommender import *
MahoutArtistRecommender.import_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_recommendations.csv')

# evaluate the recommendations  
from lastfm.mahout_recommender import *
from lastfm.evaluation import *
ArtistRecommenderEvaluator.evaluate_recommendations(MahoutArtistRecommender, 10)

# evaluate mahout recommender
# novel:

# export training data
from lastfm.mahout_recommender import *
NovelMahoutArtistRecommender.export_data('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_train.csv')

# run mahout train, test -> lastfm_recommendations.csv
cd ../mahout/mahoutrec
./unresystrecommend.sh

# import predictions
from lastfm.mahout_recommender import *
NovelMahoutArtistRecommender.import_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_recommendations.csv')

# evaluate the recommendations  
from lastfm.mahout_recommender import *
from lastfm.evaluation import *
NovelArtistRecommenderEvaluator.evaluate_recommendations(NovelMahoutArtistRecommender, 10)


# Flixster
#
#

# select test data - obecne
from flixster.evaluation import *
MovieRecommenderEvaluator.select_evaluation_pairs()

# evaluate mahout recommender - predictions:
#

# export training data
from flixster.mahout_recommender import *
MahoutMovieRecommender.export_data('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/flixster_train.csv')

# export test data
from flixster.evaluation import *
MovieRecommenderEvaluator.export_evaluation_pairs('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/flixster_test.csv')

# run mahout train, test -> lastfm_predictions.csv
cd ../mahout/mahoutrec
./unresystpredict.sh flixster

# import predictions
from flixster.mahout_recommender import *
MahoutMovieRecommender.import_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/flixster_predictions.csv')

# evaluate the predictions  
from flixster.mahout_recommender import *
from flixster.evaluation import *
MovieRecommenderEvaluator.evaluate_predictions(MahoutMovieRecommender)


# evaluate mahout recommender - recommendations
# 

# export training data
from flixster.mahout_recommender import *
MahoutMovieRecommender.export_data('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/flixster_train.csv')

# run mahout train, test -> flixster_recommendations.csv
cd ../mahout/mahoutrec
./unresystrecommend.sh flixster

# import predictions
from flixster.mahout_recommender import *
MahoutMovieRecommender.import_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/flixster_recommendations.csv')

# evaluate the recommendations  
from flixster.mahout_recommender import *
from flixster.evaluation import *
MovieRecommenderEvaluator.evaluate_recommendations(MahoutMovieRecommender, 10)

# Travel
#
#

# select test data - obecne
from travel.models import *
TourOrderEvalPair.select()

# evaluate mahout recommender - recommendations
# 

# export training data
from travel.mahout_recommender import *
MahoutOrderTourRecommender.export_data('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/travel_train.csv')

# run mahout train, test -> travel_recommendations.csv
cd ../mahout/mahoutrec
./unresystrecommend.sh travel 

# import predictions
from travel.mahout_recommender import *
MahoutOrderTourRecommender.import_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/travel_recommendations.csv')

# evaluate the recommendations  
from travel.mahout_recommender import *
from travel.evaluation import *
OrderTourRecommenderEvaluator.evaluate_recommendations(MahoutOrderTourRecommender, 10)
