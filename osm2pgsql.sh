#!/bin/bash

echo "Run as $0 <STYLE-File> <PBF-File>"
# Example: /vagrant/osm2pgsql.sh default.style vienna.osm.pbf

# docker args:
# -i, -t: run interactively
# --rm: remove after done
# --link: connect to postgres-osm container
# -v: load /vagrant/osm_data into container
# -c: command to run

# osm2pgsql args:
# -c: create
# -d: Database
# -U: postgres-username
# -H: postgres-host
# -S: Style-file (followed by pbf file)

echo "Running inside container ..."
echo "osm2pgsql -c -d gis -U postgres -H pg -S /osm/$1 /osm/$2"

docker run -i -t --rm \
           --link postgres-osm:pg \
           -v /vagrant/osm_data:/osm \
           sigita42/postgres-osm-tools \
           -c "osm2pgsql -c -d gis -U osm -H pg --cache 800 -S /osm/$1 /osm/$2"