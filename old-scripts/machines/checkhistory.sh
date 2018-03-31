cd ~/machines/check/

rm ping.sh
rm ping.out
rm marauder.sh

cat ips.csv | ./getevery.py > ping.sh
chmod u+x ping.sh
./ping.sh | tee ping.out
cat ping.out | ./filterhistory.py > marauder.sh
chmod u+x ./marauder.sh
./marauder.sh | tee ~/history.txt

