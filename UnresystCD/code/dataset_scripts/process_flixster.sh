sort -n links.txt -o slinks.txt
sort -n ratings.txt -o sratings.txt

head -15000 sratings.txt > mini/ratings.tsv
head -105000 slinks.txt > mini/links.tsv

