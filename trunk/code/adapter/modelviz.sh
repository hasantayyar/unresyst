#/bin/bash

# 1 argument: the application name for which models visualization should be performed
# there must exist the 'modelvizs' directory

python modelviz.py $1 > $1.dot
dot $1.dot -Tpng -o modelvizs/$1.png
rm $1.dot
eog modelvizs/$1.png 
