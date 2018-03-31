./getusage.py >> query.sh
chmod u+x query.sh
./query.sh | ./usagefilter.py >> usage.txt
rm query.sh
