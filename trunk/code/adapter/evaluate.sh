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



# evaluate novel mahout recommender:
# 

# export training data
from lastfm.mahout_recommender import *
NovelMahoutArtistRecommender.export_data('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_train.csv')

# export test data
from lastfm.evaluation import *
NovelArtistRankEvaluator.export_evaluation_pairs('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_test.csv')

# run mahout train, test -> lastfm_predictions.csv
cd ../mahout/mahoutrec
./unresystpredict.sh lastfm

# import predictions
from lastfm.mahout_recommender import *
NovelMahoutArtistRecommender.import_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_predictions.csv')

# evaluate the predictions  
from lastfm.mahout_recommender import *
from lastfm.evaluation import *
NovelArtistRankEvaluator.evaluate_predictions(NovelMahoutArtistRecommender)

# evaluate nenovel mahout recommender:
# 

# export training data
from lastfm.mahout_recommender import *
MahoutArtistRecommender.export_data('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_train.csv')

# export test data
from lastfm.evaluation import *
ArtistRankEvaluator.export_evaluation_pairs('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_test.csv')

# run mahout train, test -> lastfm_predictions.csv
cd ../mahout/mahoutrec
./unresystpredict.sh lastfm

# import predictions
from lastfm.mahout_recommender import *
MahoutArtistRecommender.import_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_predictions.csv')

# evaluate the predictions  
from lastfm.mahout_recommender import *
from lastfm.evaluation import *
ArtistRankEvaluator.evaluate_predictions(MahoutArtistRecommender)



# below
#

# build, 
#save_all_to_predictions must be true
./build.sh lastfm

# evaluate and save the predictions
from lastfm.evaluation import *
from lastfm.recommender import *
NovelArtistRecommenderEvaluator.evaluate_predictions(NovelArtistRecommender, save_predictions=True)

# export predictions
from lastfm.recommender import *
NovelArtistRecommender.export_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_train.csv')

# export test data
from lastfm.evaluation import *
NovelArtistRankEvaluator.export_evaluation_pairs('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_test.csv')

# run mahout train, test -> flixster_predictions.csv
cd ../mahout/mahoutrec
./unresystpredict.sh lastfm

# update unresyst predictions with the obtained
from lastfm.recommender import *
NovelArtistRecommender.update_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_predictions.csv')

# run evaluation
./lastfmeval.sh novel dontbuild



# recommendations - netreba
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


# hybrid
#

# build save_all_to_predictions must be true
./build.sh flixster

# export as usual

# export training data
from flixster.mahout_recommender import *
MahoutMovieRecommender.export_data('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/flixster_train.csv')

# export test data
from flixster.evaluation import *
MovieRecommenderEvaluator.export_evaluation_pairs('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/flixster_test.csv')

# run mahout train, test -> flixster_predictions.csv
cd ../mahout/mahoutrec
./unresystpredict.sh flixster

# evaluate what we have and save the predictions
from flixster.evaluation import *
from flixster.recommender import *
MovieRecommenderEvaluator.evaluate_predictions(MovieRecommender, save_predictions=True)

# update unresyst predictions with the obtained
from flixster.recommender import *
MovieRecommender.update_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/flixster_predictions.csv')

# run evaluation
./flixstereval.sh preds dontbuild


# below
#

# build, 
#save_all_to_predictions must be true
./build.sh flixster

# evaluate and save the predictions
from flixster.evaluation import *
from flixster.recommender import *
MovieRecommenderEvaluator.evaluate_predictions(MovieRecommender, save_predictions=True)

# export predictions
from flixster.recommender import *
MovieRecommender.export_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/flixster_train.csv')

# export test data
from flixster.evaluation import *
MovieRecommenderEvaluator.export_evaluation_pairs('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/flixster_test.csv')

# run mahout train, test -> flixster_predictions.csv
cd ../mahout/mahoutrec
./unresystpredict.sh flixster

# import predictions
from flixster.mahout_recommender import *
MahoutMovieRecommender.import_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/flixster_predictions.csv')

# evaluate the predictions  
from flixster.mahout_recommender import *
from flixster.evaluation import *
MovieRecommenderEvaluator.evaluate_predictions(MahoutMovieRecommender)


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

# evaluate mahout recommender - predictions
# 

# export training data
from travel.mahout_recommender import *
MahoutOrderTourRecommender.export_data('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/travel_train.csv')

# export test data
from travel.evaluation import *
OrderTourRecommenderEvaluator.export_evaluation_pairs('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/travel_test.csv')

# run mahout train, test -> travel_recommendations.csv
cd ../mahout/mahoutrec
./unresystpredict.sh travel 

# import predictions
from travel.mahout_recommender import *
MahoutOrderTourRecommender.import_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/travel_predictions.csv')

# evaluate the predictions
from travel.evaluation import *
from travel.mahout_recommender import *
OrderTourRankEvaluator.evaluate_predictions(MahoutOrderTourRecommender)


# below
#

# build, 
#save_all_to_predictions must be true
./build.sh travel

# evaluate and save the predictions
from travel.evaluation import *
from travel.recommender import *
OrderTourRecommenderEvaluator.evaluate_predictions(OrderTourRecommender, save_predictions=True)

# export predictions
from travel.recommender import *
OrderTourRecommender.export_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/travel_train.csv')

# export test data
from travel.evaluation import *
OrderTourRecommenderEvaluator.export_evaluation_pairs('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/travel_test.csv')

# run mahout train, test -> flixster_predictions.csv
cd ../mahout/mahoutrec
./unresystpredict.sh travel

# update unresyst predictions with the obtained
from travel.recommender import *
OrderTourRecommender.update_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/travel_predictions.csv')

# run evaluation
./traveleval.sh preds dontbuild
















#############################

# import predictions
from travel.mahout_recommender import *
MahoutOrderTourRecommender.import_predictions('/home/pcv/diplomka2/svn/trunk/code/adapter/csv/travel_predictions.csv')

# evaluate the predictions  
from travel.mahout_recommender import *
from travel.evaluation import *
OrderTourRankEvaluator.evaluate_predictions(MahoutOrderTourRecommender)

