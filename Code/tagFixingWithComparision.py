'''
This script is supposed to work mainly with tables made from names_with_constraints or distinct_repeated_ref views for checking tags or can be applied to the general highway table. Previously mentioned views contain roads with references that correspond to more than one highway name.
This script finds names that exist in both versions, written together and separate. For example "Ostautobahn" and "Ost Autobahn". If such highway exists, it assumes that the version written separately is the correct one and updates all the table rows that have the same name  written together. The check was intended to keep data consistent and have names written in exactly the same manner.
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
    cur.execute("""SELECT * from names_selected""")
except:
    print "I can't SELECT from names_selected"

# defines the first split function
def split_words(text, id, list):
    list = list.append({"highway": text.split(), "id": id})

rows = cur.fetchall()

# patterns to recognize correct and wrong versions of tags
pattern = re.compile('^[a-zA-ZäöüßÄÖÜ]+ Autobahn$')
pattern2 = re.compile('^[a-zA-ZäöüßÄÖÜ]+autobahn$')

matches = []
matches2 = []
splitwords = []
splitwords2 = []
result = []

# append to matches list all the correct highways
for row in rows:
    if pattern.match(row["name"]):
        matches.append({"highway": row["name"], "id": row["id"]})

# append to matches2 list all the wrong highways
for row in rows:
    if pattern2.match(row["name"]):
        matches2.append({"highway": row["name"], "id": row["id"]})

# split all the correct highway names to extract the main name (preparing for comparison)
for match in matches:
    split_words(match["highway"], match["id"], splitwords)

# split all the wrong highway names to extract the main name (preparing for comparison)
for match2 in matches2:
    splitwords2.append({"highway": re.split("autobahn",match2["highway"]), "id": match2["id"]})

# comparing the main names of correct and wrong highways.
# If they match, save their id to be able replace right for wrong later.
for splitword in splitwords:
    for splitword2 in splitwords2:
        if splitword["highway"][0] == splitword2["highway"][0]:
            result.append({"finalname": splitword["highway"][0] + ' Autobahn', "id_correct_name": splitword["id"], "id_wrong_name": splitword2["id"]})

# Update the table with correct names
try:
    for item in result:
        finalname = item['finalname']
        identity = item['id_wrong_name']
        cur.execute("UPDATE names_selected SET name = %s WHERE id = %s", (finalname, identity))
    conn.commit()

    print "Number of rows updated: %d" % cur.rowcount

except psycopg2.DatabaseError, e:
    if conn:
        conn.rollback()
    print 'Error %s' % e
    sys.exit(1)

if conn:
    conn.close()

