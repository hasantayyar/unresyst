#!/bin/sh

# params:
# lastfm
# flixster
# travel


LASTFM=false
FLIXSTER=false
TRAVEL=false

for param in $*;
do    
    case $param in
    'lastfm')
        LASTFM=true
        ;;
    'flixster')
        FLIXSTER=true
        ;;
    'travel')
        TRAVEL=true
        ;;        
    esac
done

if [ $LASTFM = true ]
then
    mvn -e exec:java -Dexec.mainClass="com.unresyst.UnresystPredict"  -Dexec.args="/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_train.csv /home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_test.csv /home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_predictions.csv" 
fi

if [ $FLIXSTER = true ]
then
    mvn -e exec:java -Dexec.mainClass="com.unresyst.UnresystPredict"  -Dexec.args="/home/pcv/diplomka2/svn/trunk/code/adapter/csv/flixster_train.csv /home/pcv/diplomka2/svn/trunk/code/adapter/csv/flixster_test.csv /home/pcv/diplomka2/svn/trunk/code/adapter/csv/flixster_predictions.csv" 
fi


if [ $TRAVEL = true ]
then
    mvn -e exec:java -Dexec.mainClass="com.unresyst.UnresystPredict"  -Dexec.args="/home/pcv/diplomka2/svn/trunk/code/adapter/csv/travel_train.csv /home/pcv/diplomka2/svn/trunk/code/adapter/csv/travel_test.csv /home/pcv/diplomka2/svn/trunk/code/adapter/csv/travel_predictions.csv" 
fi


echo ""
