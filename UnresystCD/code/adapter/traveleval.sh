#!/bin/sh



BUILD=true
EVAL=''
REC=''
RECS=false
PREDS=false

for param in $*;
do    
    case $param in
    'recs')
        EVAL='OrderTourRecommenderEvaluator'
        REC='OrderTourRecommender'
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
    echo "from travel.recommender import *; OrderTourRecommender.build()" | python ./manage.py shell
fi

if [ $RECS = true ]
then
    echo "Evaluating recommendations..."
    echo "from travel.evaluation import *; from travel.recommender import *; $EVAL.evaluate_recommendations($REC, 10); quit()"| python ./manage.py shell
fi

if [ $PREDS = true ]
then
    echo "Evaluating predicitons..."
    echo "from travel.evaluation import *; from travel.recommender import *; OrderTourRankEvaluator.evaluate_predictions(OrderTourRecommender); quit()" | python ./manage.py shell
fi



echo ""

