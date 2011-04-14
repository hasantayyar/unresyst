
find ./ -iname '*.py' | xargs -n 1 wc -l | cut -d' ' -f1 | (SUM=0; while read NUM; do SUM=$(($SUM+$NUM)); done; echo $SUM)
