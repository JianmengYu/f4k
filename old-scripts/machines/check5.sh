
cd ~/machines/check/
cat ips.csv | ./get5.py > ping.sh
chmod u+x ping.sh
./ping.sh | tee ping.out
cat ping.out | ./filter.py > marauder.sh
chmod u+x ./marauder.sh
./marauder.sh | tee marauder.out
cat marauder.out | ./marauderfilter.py | tee ~/machines/hosts.out

rm ping.sh
rm ping.out
rm marauder.sh
rm marauder.out
