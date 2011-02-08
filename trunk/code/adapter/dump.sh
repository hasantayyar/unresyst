#!/bin/sh

# dump the database to given file
mysqldump --opt -u root adapter > $1
