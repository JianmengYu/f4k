rm hosts.out
cat ips.csv | ./get606.py > marauder.sh
chmod u+x marauder.sh
./marauder.sh > marauder.out
cat marauder.out | ./marauderfilter.py > hostssetting.sh
chmod u+x hostssetting.sh
source ./hostssetting.sh | tee hosts.out
rm marauder.sh
