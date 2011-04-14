grep diplomka_time_order travel.sql -m 1 -n

# shorten, remove unused
tail -n +38 diplomka\(2\).sql > travel1.sql 
head -n 302073 travel1.sql > travel2.sql

# away with the insert part 
sed -e 's/.*(//' travel2.sql > travel3.sql 

# away with the end 
sed -e 's/);.*//' travel3.sql > travel4.sql 

# remove ', ' from places between appostrophes
sed -e "s/', '\(.[^']*\),\([^']*\)', '/', '\1\2', '/" travel4.sql > travel5.sql
sed -e "s/', '\(.[^']*\),\([^']*\)', '/', '\1\2', '/" travel5.sql > travel6.sql
sed -e "s/', '\(.[^']*\),\([^']*\)', '/', '\1\2', '/" travel6.sql > travel7.sql

# away with spaces behind commas 
sed -e 's/, /,/g' travel7.sql > travel8.sql

# away with appostrophes 
sed -e "s/'//g" travel8.sql > travel9.sql

