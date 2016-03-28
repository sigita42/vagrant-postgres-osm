'''
We don't have to check for repeated ref values for different names because the table is created in a way, that every name can have only one certain ref value.
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
    cur.execute("""SELECT distinct new_name, old_name, ref from old_new_names""")

except:
    print "I can't SELECT from the table"

rows = cur.fetchall()

# array for all inconsistent highway names
singleAppear = []
inconsist = []
##### NOT sure if this works yet! need to check again
# count the appearance of distinct old_names and new_names
appearances = defaultdict(int)

for row in rows:
    appearances[row["old_name"]] += 1

# collect all the inconsistently named highway references in inconsist list
for key, value in appearances.iteritems():
    if value == 1:
        singleAppear.append(key)
    elif value >1:
        inconsist.append(key)

# check if inconsist list is empty or not
# print the ref values of inconsistently names highways
if inconsist:
    print "These segments have more than 1 corresponding new_name! Visual check or other renaming solution necessary!"
    for old_name in inconsist:
        print old_name
elif not inconsist:
    print "There were no repeated old_name and new_name combinations. Lucky you! :)"
else:
    print "Something went wrong!"

refHolder = []
# collect all names that don't have a reference in table old_new_names
# (these are not all the names overall without ref)
for row in rows:
    if row["old_name"] in singleAppear:
        refHolder.append({"old_name": row["old_name"], "new_name": row["new_name"], "ref": row["ref"]})

# select
try:
    cur.execute("""SELECT name, ref from planet_osm_highways_no_links""")

except:
    print "I can't SELECT from the table"

rows = cur.fetchall()

# update highway table
try:
    for highway in refHolder:
        refval = highway["ref"]
        name = highway["new_name"]
        old_name = highway["old_name"]
        cur.execute("UPDATE planet_osm_highways_no_links SET name = %s, ref = %s WHERE name = %s", (name, refval, old_name))
        cur.execute("UPDATE planet_osm_highways_no_links SET ref = %s WHERE name = %s and ref is null", (refval, name))
    conn.commit()

    print "Number of rows updated: %d" % cur.rowcount

except psycopg2.DatabaseError, e:
    if conn:
        conn.rollback()
    print 'Error %s' % e
    sys.exit(1)

if conn:
    conn.close()