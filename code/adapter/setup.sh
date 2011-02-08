#!/bin/sh

# parametry: co chces vlozit do databaze: lastfm, demo

# drop and create database
echo "DROP DATABASE IF EXISTS adapter; CREATE DATABASE adapter CHARACTER SET utf8;" | mysql --user=root mysql

# syncdb
python ./manage.py syncdb --noinput > /dev/null

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

echo "" 
