./generatequery.py >> query.sh
chmod u+x query.sh
./query.sh | ./ipfilter.py >> ips.txt
rm query.sh
