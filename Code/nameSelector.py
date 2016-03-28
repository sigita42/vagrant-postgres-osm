'''
This script looks for parts of highway that are, for example, bridges and tunnels. It replaces these names with the actual highway names based on the same reference value, to improve consistency. Made for table planet_osm_highways_no_links.
'''
import os
import sys
from qgis.core import *
from qgis.gui import *
import psycopg2
import psycopg2.extras
import re
from collections import defaultdict
#from repeatedNameCheck import repeatedNameCheck

try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    print "I am connected to database"
except:
    print "I am unable to connect to the database"

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
# select names that include 'Autobahn'
try:
    cur.execute("""SELECT distinct name, ref from planet_osm_highways_no_links where name like '%Autobahn%' and ref is not null""")

except:
    print "I can't SELECT from the table"

rows = cur.fetchall()

lookUpList = []
# collect all names that include 'Autobahn' in a list
for row in rows:
    lookUpList.append({"name": row["name"], "ref": row["ref"]})

if conn:
    conn.close()

try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    print "I am connected to database"
except:
    print "I am unable to connect to the database"

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

try:
    cur.execute("""SELECT name, ref, osm_id from planet_osm_highways_no_links where name like '%Autobahn%' and ref is null""")

except:
    print "I can't SELECT from the table"

rows = cur.fetchall()

def refReplacer(referenceList, rows):
    try:
        for item in referenceList:
            refVal = item["ref"]
            for row in rows:
                name = row["name"]
                if row["name"] == item["name"]:
                    cur.execute("UPDATE planet_osm_highways_no_links SET ref = %s WHERE name = %s", (refVal, name))
        conn.commit()
    except psycopg2.DatabaseError, e:
        if conn:
            conn.rollback()
        print 'Error %s' % e
        sys.exit(1)

refReplacer(lookUpList, rows)

if conn:
    conn.close()

##############################

try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    print "I am connected to database"
except:
    print "I am unable to connect to the database"

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
# select names
# it is important that it selects only distinct names that are not null because
# otherwise on the function repeatedNameCheck it would conclude that also names
# that have 1 reference value and one null value, have more than 1 reference values
try:
    cur.execute("""SELECT distinct name, ref from planet_osm_highways_no_links where
    (name like '%brücke%'
    or name like '%Brücke%'
    or name like '%tunnel%'
    or name like '%Tunnel%'
    or name like '%talübergang'
    or name like '%Talübergang%'
    or name like '%Hochstraße%'
    or name like '%hochstraße%') and ref is not null""")

except:
    print "I can't SELECT from the table"

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
    return inconsistent

inconsistent = repeatedNameCheck(conn, rows)

lookUpListParts = []

for row in rows:
    if row["name"] not in inconsistent:
        lookUpListParts.append({"name":row["name"], "ref":row["ref"]})

if conn:
    conn.close()

try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    print "I am connected to database"
except:
    print "I am unable to connect to the database"

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

try:
    cur.execute("""SELECT distinct name, ref from planet_osm_highways_no_links where
    (name like '%brücke%'
    or name like '%Brücke%'
    or name like '%tunnel%'
    or name like '%Tunnel%'
    or name like '%talübergang'
    or name like '%Talübergang%'
    or name like '%Hochstraße%'
    or name like '%hochstraße%')
    and ref is null""")

except:
    print "I can't SELECT from the table"

rows = cur.fetchall()

refReplacer(lookUpListParts, rows)

if conn:
    conn.close()
################################

try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    print "I am connected to database"
except:
    print "I am unable to connect to the database"

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# select names that exclude 'Autobahn'
try:
    cur.execute("""SELECT name, ref from planet_osm_highways_no_links where name not like '%Autobahn%' and ref != 'A5'""")

except:
    print "I can't SELECT from the table"

rows = cur.fetchall()

for item in lookUpList:
    for part in lookUpListParts:
        if part["ref"] == item["ref"] and part["name"] != item["name"]:
            newName = item["name"]
            ref = item["ref"]
            for row in rows:
                try:
                    cur.execute("UPDATE planet_osm_highways_no_links SET name = %s WHERE ref = %s", (newName, ref))
                    conn.commit()

                except psycopg2.DatabaseError, e:
                    if conn:
                        conn.rollback()
                    print 'Error %s' % e
                    sys.exit(1)

if conn:
    conn.close()
###################################
try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    print "I am connected to database"
except:
    print "I am unable to connect to the database"

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# select segments that have no name but that are also don't belong to A5 (segments that don't have special parts and have no name, didn't get their name updated in the last step. Therefore, this step.) --> shouldn't it be A23??? Why did i exclude Nord Autobahn?
try:
    cur.execute("""SELECT name, ref from planet_osm_highways_no_links where name is null and ref != 'A5'""")

except:
    print "I can't SELECT from the table"

rows = cur.fetchall()

for row in rows:
    for item in lookUpList:
        if item["ref"] == row["ref"]:
            newName = item["name"]
            ref = item["ref"]
            try:
                cur.execute("UPDATE planet_osm_highways_no_links SET name = %s WHERE ref = %s", (newName, ref))
                conn.commit()

            except psycopg2.DatabaseError, e:
                if conn:
                    conn.rollback()
                print 'Error %s' % e
                sys.exit(1)

if conn:
    conn.close()


###########################################



