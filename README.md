# vagrant-postgres-osm
Preconfigured vagrant VM with docker-postgres-osm(-tools)

## Usage? (to be written)

You should uncompress highways.zip

### start docker container with osm_tools

this create a temporary image with osm-tools pre installed. It needs to be linked to the postgres database in order to import the data

    docker run -i -t --rm --link postgres-osm:pg -v PATH_TO_OSM_DATA:/osm sigita42/postgres-osm-tools

### inside the container

to import osm data to postgres, use osm2pgsql tool like followed:

    osm2pgsql -c -d gis -U osm -H pg --cache-strategy sparse --keep-coastlines --latlong --hstore -S /osm/STYLE_FILE /osm/PBF_FILE