rm -rf NYBus_GTFS
mkdir NYBus_GTFS

for file in {manhattan,bronx,brooklyn,queens,staten_island}; do
	rm -rf $file"_GTFS"
	wget -O $file"_GTFS.zip" "http://web.mta.info/developers/data/nyct/bus/google_transit_"$file".zip"
	unzip $file"_GTFS.zip" -d $file"_GTFS"
	rm $file"_GTFS.zip"
	tail -n+2 $file"_GTFS/routes.txt" >> NYBus_GTFS/routes.txt
done;
