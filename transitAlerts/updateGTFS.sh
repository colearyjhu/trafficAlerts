wget http://www.mbta.com/uploadedfiles/MBTA_GTFS.zip
rm -rf MBTA_GTFS
unzip MBTA_GTFS.zip -d MBTA_GTFS
rm MBTA_GTFS.zip

wget -O Chicago_GTFS.zip http://www.transitchicago.com/downloads/sch_data/google_transit.zip
rm -rf Chicago_GTFS
unzip Chicago_GTFS.zip -d Chicago_GTFS
rm Chicago_GTFS.zip

wget -O DC_GTFS.zip http://www.gtfs-data-exchange.com/agency/dc-circulator/latest.zip
rm -rf DC_GTFS
unzip DC_GTFS.zip -d DC_GTFS
rm DC_GTFS.zip

wget http://www.gtfs-data-exchange.com/agency/san-francisco-municipal-transportation-agency/latest.zip
rm -rf SFMTA_GTFS
unzip latest.zip -d SFMTA_GTFS
rm latest.zip

wget http://www.bart.gov/dev/schedules/google_transit.zip
rm -rf BART_GTFS
unzip google_transit.zip -d BART_GTFS
rm google_transit.zip

rm -rf SanFran_GTFS
mkdir SanFran_GTFS
cat  SFMTA_GTFS/routes.txt > SanFran_GTFS/routes.txt
tail -n+2 BART_GTFS/routes.txt >> SanFran_GTFS/routes.txt


wget -O LIRR_GTFS.zip http://web.mta.info/developers/data/lirr/google_transit.zip
rm -rf LIRR_GTFS
unzip LIRR_GTFS.zip -d  LIRR_GTFS
rm LIRR_GTFS.zip

wget -O MNR_GTFS.zip http://web.mta.info/developers/data/mnr/google_transit.zip
rm -rf MNR_GTFS
unzip MNR_GTFS.zip -d  MNR_GTFS
rm MNR_GTFS.zip

wget -O Subway_GTFS.zip http://web.mta.info/developers/data/nyct/subway/google_transit.zip
rm -rf Subway_GTFS
unzip Subway_GTFS.zip -d  Subway_GTFS
rm Subway_GTFS.zip


rm -rf NY_GTFS
mkdir NY_GTFS
cat MNR_GTFS/routes.txt > NY_GTFS/routes.txt
sed 's/,"",/,"LIRR","",/' LIRR_GTFS/routes.txt| tail -n+2 >> NY_GTFS/routes.txt
sed -e 's/MTA NYCT,//' -e 's/,/,MTA NYCT,/' Subway_GTFS/routes.txt | tail -n+2>> NY_GTFS/routes.txt

for file in {manhattan,bronx,brooklyn,queens,staten_island}; do
        rm -rf $file"_GTFS"
        wget -O $file"_GTFS.zip" "http://web.mta.info/developers/data/nyct/bus/google_transit_"$file".zip"
        unzip $file"_GTFS.zip" -d $file"_GTFS"
        rm $file"_GTFS.zip"
        tail -n+2 $file"_GTFS/routes.txt" >> NY_GTFS/routes.txt
done;
