#!/bin/sh

# parametry: 
#  co chces vlozit do databaze: lastfm, demo
#  dontdrop: pokud se preda, nedropuje se databaze


LASTFM=false
DEMO=false
FLIXSTER=false
DONTDROP=false
TRAVEL=false

for param in $*;
do    
    case $param in
    'lastfm')
        LASTFM=true
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
    'dontdrop')
        DONTDROP=true
        ;;
    esac
done

if [ $DONTDROP = false ]
then
    # drop and create database
    echo "Dropping and creating database."
    echo "DROP DATABASE IF EXISTS adapter; CREATE DATABASE adapter CHARACTER SET utf8;" | mysql --user=root mysql
fi

# syncdb
python ./manage.py syncdb --noinput > /dev/null


if [ $DEMO = true ]
then
    echo "Adding demo data."
    echo "from demo.save_data import save_data; save_data(); quit();" | python ./manage.py shell
fi

if [ $LASTFM = true ]
then
    echo "Adding last.fm data."
    echo "from lastfm.save_data import save_data; save_data(); quit();" | python ./manage.py shell
fi

if [ $FLIXSTER = true ]
then
    echo "Adding flixster data."
    echo "from flixster.save_data import save_data; save_data(); quit();" | python ./manage.py shell
fi

if [ $TRAVEL = true ]
then
    echo "Adding travel data."
    echo "from travel.save_data import save_data; save_data(); quit();" | python ./manage.py shell
fi

echo "" 
