#!/bin/sh

# run the evaluation- recommendations. parameters 
# recs -> recommendations
# preds -> predictions
# dontbuild-> don't build

BUILD=true
RECS=false
PREDS=false

for param in $*;
do    
    case $param in
    'recs')
        RECS=true
        ;;
    'preds')
        PREDS=true
        ;;
    'dontbuild')
        BUILD=false
        ;;
    esac
done

if [ $BUILD = true ]
then
    # build
    echo "Building..."
    echo "from flixster.recommender import *; MovieRecommender.build()" | python ./manage.py shell
fi

if [ $RECS = true ]
then
    echo "Evaluating recommendations..."
    echo "from flixster.evaluation import *; from flixster.recommender import *; MovieRecommenderEvaluator.evaluate_recommendations(MovieRecommender, 10)"| python ./manage.py shell
fi

if [ $PREDS = true ]
then
    echo "Evaluating predictions..."
    echo "from flixster.evaluation import *; from flixster.recommender import *; MovieRecommenderEvaluator.evaluate_predictions(MovieRecommender)"| python ./manage.py shell
fi

echo ""

