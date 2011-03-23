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
    mvn -e exec:java -Dexec.mainClass="com.unresyst.UnresystRecommend"  -Dexec.args="/home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_train.csv 10 /home/pcv/diplomka2/svn/trunk/code/adapter/csv/lastfm_recommendations.csv" 
fi

if [ $FLIXSTER = true ]
then
    mvn -e exec:java -Dexec.mainClass="com.unresyst.UnresystRecommend"  -Dexec.args="/home/pcv/diplomka2/svn/trunk/code/adapter/csv/flixster_train.csv 10 /home/pcv/diplomka2/svn/trunk/code/adapter/csv/flixster_recommendations.csv" 
fi

if [ $TRAVEL = true ]
then
    mvn -e exec:java -Dexec.mainClass="com.unresyst.UnresystRecommend"  -Dexec.args="/home/pcv/diplomka2/svn/trunk/code/adapter/csv/travel_train.csv 10 /home/pcv/diplomka2/svn/trunk/code/adapter/csv/travel_recommendations.csv" 
fi

echo ""
