#!/bin/bash

# Example: /vagrant/osm_tools.sh
# afterwards run osmosis or osm2pgsql inside that container
# always store the results in /osm_data to be able to retrieve them later on

# docker args:
# -i, -t: run interactively
# --rm: remove after done
# --link: connect to postgres-osm container
# -v: load /vagrant/osm_data into container
# -c: command to run

docker run -i -t --rm \
           --link postgres-osm:pg \
           -v /vagrant/osm_data:/osm_data \
           sigita42/postgres-osm-tools