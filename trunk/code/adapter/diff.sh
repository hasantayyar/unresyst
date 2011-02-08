#!/bin/bash

# diffovat v meldu zmenene soubory.
svn diff --diff-cmd meld `svn stat | grep "M      " | sed -e 's/M      //'`

