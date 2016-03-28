'''
This script assumes that ll highway names should be written separately like "Ost Autobahn", instead of "Ostautobahn". Therefore, it doesn't check if both versions of the names exist i the database. The script just looks for wrong tags like "Ostautobahn", "Ost autobahn" and "OstAutobahn" and replaces them in the table with "Ost Autobahn". After this script a check is necessary to see if any further inconsistencies are present.
Note: As this script uses pattern matching, table selected and used by this script should not contain null values in column "name"!
'''

import os
import sys
from qgis.core import *
from qgis.gui import *
import psycopg2
import psycopg2.extras
import re

###### connect to database to retrieve non-spatial tables ######
try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    print "I am connected to database"
except:
    print "I am unable to connect to the database"

# cursor factory added so instead of numeric row representation, a dictionary could be used
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

try:
    cur.execute("""SELECT osm_id, name, ref from planet_osm_highways_no_links where name is not null""")
except:
    print "I can't SELECT from the table"

# defines the split function
# splits on cases like 'Ostautobahn', 'OstAutobahn' and 'Ost autobahn'
def split_words(text, osm_id, list):
    list = list.append({"highway": re.split(" *(?i)autobahn", text), "osm_id": osm_id})

rows = cur.fetchall()

# patterns to recognize the wrong versions of tags
# pattern is looking for names like 'Ostautobahn'and 'OstAutobahn'
pattern = re.compile('^\w+(?i)autobahn$', re.UNICODE)
# pattern is looking for names like 'Ost autobahn'
pattern2 = re.compile('^\w+ autobahn$', re.UNICODE)

matches = []
splitwords = []
result = []

# append to matches list all the wrongly tagged highways
for row in rows:
    if pattern.match(row["name"]) or pattern2.match(row["name"]):
        matches.append({"highway": row["name"], "osm_id": row["osm_id"]})

# split all the wrong highway names to extract the main name (like 'Ost' in case of 'Ostautobahn')
for match in matches:
    split_words(match["highway"], match["osm_id"], splitwords)

# Add to result list the main names and Autobahn in the end of the name.
# Save their id to be able to update the DB table.
for splitword in splitwords:
    result.append({"finalname": splitword["highway"][0] + ' Autobahn', "osm_id": splitword["osm_id"]})

# Update the table with correct names
try:
    for item in result:
        finalname = item['finalname']
        identity = item['osm_id']
        cur.execute("UPDATE planet_osm_highways_no_links SET name = %s WHERE osm_id = %s", (finalname, identity))
    conn.commit()

    print "Number of rows updated: %d" % cur.rowcount

except psycopg2.DatabaseError, e:
    if conn:
        conn.rollback()
    print 'Error %s' % e
    sys.exit(1)

if conn:
    conn.close()

