# build the shoe recommender

LASTFM=false
DEMO=false
ADEMO=false

for param in $*;
do    
    case $param in
    'lastfm')
        LASTFM=true
        ;;
    'demo')
        DEMO=true
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

echo ""
