rm hosts.out
rm hostssetting.sh

cat ips.csv | ./get606.py | tee ping606.sh
chmod u+x ping606.sh
./ping606.sh > ping606.out
cat ping606.out | ./filter606.py | tee marauder.sh
chmod u+x marauder.sh
./marauder.sh > marauder.out
cat marauder.out | ./marauderfilter.py | tee  hostssetting.sh
chmod u+x hostssetting.sh
source ./hostssetting.sh | tee hosts.out

rm marauder.sh
rm ping606.sh
