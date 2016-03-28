'''
Checks if there is any highway left that doesn't have any segment with 'Autobahn' or 'autobahn' in its name. To detect that it is a highway, the reference value is used ("A"+number means it is a highway).
'''
import os
import sys
from qgis.core import *
from qgis.gui import *
import psycopg2
import psycopg2.extras
import re
from collections import defaultdict

try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    print "I am connected to database"
except:
    print "I am unable to connect to the database"

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
# select
try:
    cur.execute("""SELECT name, ref FROM planet_osm_highways_no_links WHERE
    name not LIKE '%Autobahn%' AND
    name not LIKE '%autobahn' AND
    ref LIKE '%A%'
    GROUP BY ref, name""")

except:
    print "I can't SELECT from the table"

rows = cur.fetchall()

highways = []

for row in rows:
    highways.append({"name":row["name"], "ref":row["ref"]})

# check if highways list is empty or not
# print the ref values and names
if highways:
    print "These reference values do not have any name that includes word 'Autobahn'"
    for segment in highways:
        print segment
elif not highways:
    print "There are no highways left, that have a name without 'Autobahn' in it"
else:
    print "Something went wrong!"

if conn:
    conn.close()