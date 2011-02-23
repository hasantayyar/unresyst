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

# evaluate my recommender
from lastfm.evaluation import *
ArtistRecommenderEvaluator.select_evaluation_pairs()

from lastfm.recommender import *
ArtistRecommender.build()

ArtistRecommenderEvaluator.evaluate_predictions(ArtistRecommender)

from lastfm.evaluation import *
from lastfm.recommender import *
ArtistRecommenderEvaluator.evaluate_predictions(ArtistRecommender)

# evaluate mahout recommender
from lastfm.mahout_recommender import *
MahoutArtistRecommender.export_data('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_train.csv')
ArtistRecommenderEvaluator.export_evaluation_pairs('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_test.csv')

# pustit mahout train, test -> lastfm_predictions.csv

MahoutArtistRecommender.import_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_predictions.csv')
ArtistRecommenderEvaluator.evaluate_predictions(MahoutArtistRecommender)
