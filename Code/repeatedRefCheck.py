'''
This script can be used at any stage of tag fixing. It checks for inconsistently named highways.
Change table name if necessary.
'''
import os
import sys
from qgis.core import *
from qgis.gui import *
import psycopg2
import psycopg2.extras
import re
from collections import defaultdict


###### connect to database to retrieve non-spatial tables ######
try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    print "I am connected to database"
except:
    print "I am unable to connect to the database"

# cursor factory added so instead of numeric row representation, a dictionary could be used
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# select distinct combinations of names and references
try:
    cur.execute("""SELECT distinct name, ref from names_selected""")
except:
    print "I can't SELECT from names_selected"

rows = cur.fetchall()

def repeatedRefCheck( conn, rows):
    # array for all inconsistent highway names
    inconsistent = []
    # count the appearance of distinct names and reference values
    appearances = defaultdict(int)
    for row in rows:
        appearances[row["ref"]] += 1
    # collect all the inconsistently named highway references in inconsist list
    for key, value in appearances.iteritems():
        if value > 1:
            inconsistent.append(key)
    # check if inconsist list is empty or not
    # print the ref values of inconsistently names highways
    if not inconsistent:
        print "ALL reference values have ONLY ONE corresponding name."
    elif inconsistent:
        print "Following reference values have MORE THAN ONE name: "
        for ref in inconsistent:
            print ref
    else:
        print "something went wrong!"
    if conn:
        conn.close()

repeatedRefCheck(conn, rows)

