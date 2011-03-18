#!/bin/sh

# dump the database to given file (relative from ../db/dumps/)
mysqldump --opt -u root adapter > ../db/dumps/$1

echo "dumped to ../db/dumps/$1"
