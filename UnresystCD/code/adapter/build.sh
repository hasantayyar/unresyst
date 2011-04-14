# build the shoe recommender

LASTFM=false
NLASTFM=false
DEMO=false
ADEMO=false
FLIXSTER=false
TRAVEL=false

for param in $*;
do    
    case $param in
    'lastfm')
        LASTFM=true
        ;;
    'nlastfm')
        NLASTFM=true
        ;;
    'demo')
        DEMO=true
        ;;
    'flixster')
        FLIXSTER=true
        ;;
    'travel')
        TRAVEL=true
        ;;
    'ademo')
        ADEMO=true
        ;;        
    esac
done

if [ $DEMO = true ]
then
    echo "from demo.recommender import ShoeRecommender; ShoeRecommender.build(); quit();" | python ./manage.py shell
fi

if [ $ADEMO = true ]
then
    echo "from demo.recommender import AverageRecommender; AverageRecommender.build(); quit();" | python ./manage.py shell
fi

if [ $LASTFM = true ]
then
    echo "from lastfm.recommender import ArtistRecommender; ArtistRecommender.build(); quit();" | python ./manage.py shell
fi

if [ $NLASTFM = true ]
then
    echo "from lastfm.recommender import NovelArtistRecommender; NovelArtistRecommender.build(); quit();" | python ./manage.py shell
fi

if [ $FLIXSTER = true ]
then
    echo "from flixster.recommender import MovieRecommender; MovieRecommender.build(); quit();" | python ./manage.py shell
fi

if [ $TRAVEL = true ]
then
    echo "from travel.recommender import OrderTourRecommender; OrderTourRecommender.build(); quit();" | python ./manage.py shell
fi

echo ""
