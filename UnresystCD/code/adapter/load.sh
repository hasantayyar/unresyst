#!/bin/sh

# load the database from the given file
mysql -u root adapter < $1
