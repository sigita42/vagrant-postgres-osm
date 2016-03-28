'''
This script can be used at any stage of tag fixing. It checks for highway names that have more than one ref value.
'''
import os
import sys
from qgis.core import *
from qgis.gui import *
import psycopg2
import psycopg2.extras
from collections import defaultdict

###### connect to database ######
try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    print "I am connected to database"
except:
    print "I am unable to connect to the database"

# cursor factory added so instead of numeric row representation, a dictionary could be used
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# select distinct combinations of names and references
try:
    cur.execute("""SELECT distinct name, ref from planet_osm_highways_no_links
where ref not like '%S%' and name not like 'Grünbrücke'""")

except:
    print "I can't SELECT from names_selected"

rows = cur.fetchall()

def repeatedNameCheck( conn, rows):
    # array for all inconsistent highway names
    inconsistent = []
    # count the appearance of distinct names and reference values
    appearances = defaultdict(int)
    for row in rows:
        appearances[row["name"]] += 1
    # collect all the inconsistently named highway names in inconsist list
    for key, value in appearances.iteritems():
        if value > 1:
            inconsistent.append(key)
    # check if inconsist list is empty or not
    # print the names of inconsistent highway reference values
    if not inconsistent:
        print "ALL names have ONLY ONE corresponding reference value."
    elif inconsistent:
        print "Following names have MORE THAN ONE reference value: "
        for name in inconsistent:
            print name
    else:
        print "something went wrong!"

repeatedNameCheck(conn, rows)

if conn:
    conn.close()


