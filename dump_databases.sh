#!/bin/bash

docker exec -ti postgres-osm-vienna-old pg_dump -U postgres gis | xz > /vagrant/vienna_old_dump.xz
docker exec -ti postgres-osm-austria pg_dump -U postgres gis | xz > /vagrant/austria_dump.xz
