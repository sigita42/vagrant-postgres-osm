import os
import sys
from qgis.core import *
from qgis.gui import *
import psycopg2
import psycopg2.extras
import re
from collections import defaultdict
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import json

# list of highways with their correct names and reference values. This is used as a reference list.
# array will be moved to a separate json file
# converted from csv here http://www.convertcsv.com/csv-to-json.htm
array = '[{"ref":"A1","name":"West Autobahn","length":"292"},{"ref":"A3","name":"Süd Autobahn","length":"377"},{"ref":"A2","name":"Südost Autobahn","length":"38"},{"ref":"A4","name":"Ost Autobahn","length":"66"},{"ref":"A5","name":"Nord Autobahn","length":"24"},{"ref":"A6","name":"Nordost Autobahn","length":"22"},{"ref":"A7","name":"Mühlkreis Autobahn","length":"29"},{"ref":"A8","name":"Innkreis Autobahn","length":"76"},{"ref":"A9","name":"Pyhrn Autobahn","length":"230"},{"ref":"A10","name":"Tauern Autobahn","length":"194"},{"ref":"A11","name":"Karawanken Autobahn","length":"21"},{"ref":"A12","name":"Inntal Autobahn","length":"145"},{"ref":"A13","name":"Brenner Autobahn","length":"35"},{"ref":"A14","name":"Rheintal/Walgau Autobahn","length":"61"},{"ref":"A21","name":"Wiener Außnring Autobahn","length":"38"},{"ref":"A22","name":"Donauufer Autobahn","length":"34"},{"ref":"A23","name":"Autobahn Südosttangente Wien","length":"18"},{"ref":"A25","name":"Welser Autobahn","length":"20"},{"ref":"A26","name":"Linzer Autobahn","length":"0"},{"ref":"S1","name":"Wiener Außenring Schnellstraße","length":"40"},{"ref":"S2","name":"Wiener Nordrand Schnellstraße","length":"7"},{"ref":"S3","name":"Weinviertler Schnellstraße","length":"22"},{"ref":"S4","name":"Mattersburger Schnellstraße","length":"19"},{"ref":"S5","name":"Stockerauer Schnellstraße","length":"45"},{"ref":"S6","name":"Semmering Schnellstraße","length":"105"},{"ref":"S7","name":"Fürstenfelder Schnellstraße","length":"0"},{"ref":"S4","name":"Mattersburger Schnellstraße","length":"19"},{"ref":"S8","name":"Marchfeld Schnellstraße","length":"0"},{"ref":"S10","name":"Mühlviertler Schnellstraße","length":"10,4"},{"ref":"S16","name":"Arlberg Schnellstraße","length":"62"},{"ref":"S18","name":"Bodensee Schnellstraße","length":"0"},{"ref":"S31","name":"Burgenland Schnellstraße","length":"46"},{"ref":"S33","name":"Kremser Schnellstraße","length":"28"},{"ref":"S34","name":"Traisental Schnellstraße","length":"0"},{"ref":"S35","name":"Brucker Schnellstraße","length":"36"},{"ref":"S36","name":"Murtal Schnellstraße","length":"36"},{"ref":"S37","name":"Klagenfurter Schnellstraße","length":"18"}]'

# load the array list into a python list
highwayList = json.loads(array)

try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    print "I am connected to database"
except:
    print "I am unable to connect to the database"

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
# select names that are tagged as motorways, not part of motorway links and their name is not null
try:
    cur.execute("""SELECT distinct name, ref from planet_osm_roads where "highway"  IN ( 'motorway','motorway_link_no') and name is not null order by name""")

except:
    print "I can't SELECT from the table"

rows = cur.fetchall()

# create a list for highway names to be excluded in further operations. These are highways that have
# 100 % match between lookup list and the list against which it's been compared. This avoids false
# positive matches like Nord Autobahn and Süd Autobahn.
toExclude =[]
for row in rows:
    name = row['name']
    for record in highwayList:
        rname = record['name']
        ratio = fuzz.ratio(name, rname)
        tokenSetRatio = fuzz.token_set_ratio(name, rname)
        if ratio == 100 and tokenSetRatio == 100:
            print "this is an ABOSLUTE match:"
            print name, rname
            toExclude.append(name)

# create a comparison list that will bee checked against the lookup list
compList = []
for row in rows:
    name = row['name']
    if name not in toExclude:
        compList.append(name)

matchRatioList = []
for cname in compList:
    bestRatio = -1
    bestTokenSetRatio = -1
    comparedN = cname
    referenceN = "No match"
    # set rules for matches between highway names in lists
    for item in highwayList:
        rname = item["name"]
        ratio = fuzz.ratio(cname, rname)
        token_set_ratio = fuzz.token_set_ratio(cname, rname)
        if ratio >= 90 and token_set_ratio >= 50:
            # I'm applying this rule using only ratio because I think it's more stable algorithm
            # and the other one is more optimistic
            if ratio > bestRatio:
                bestRatio = ratio
                bestTokenSetRatio = token_set_ratio
                comparedN = cname
                referenceN = rname
        elif ratio >= 80 and token_set_ratio >= 60:
            if ratio > bestRatio:
                bestRatio = ratio
                bestTokenSetRatio = token_set_ratio
                comparedN = cname
                referenceN = rname
        elif ratio >= 70 and token_set_ratio >= 90:
            if ratio > bestRatio:
                bestRatio = ratio
                bestTokenSetRatio = token_set_ratio
                comparedN = cname
                referenceN = rname
        elif ratio >= 60 and token_set_ratio == 100:
            if ratio > bestRatio:
                bestRatio = ratio
                bestTokenSetRatio = token_set_ratio
                comparedN = cname
                referenceN = rname
    print comparedN + ",", referenceN + ",", str(bestRatio) + ",", str(bestTokenSetRatio)
    # add all the matched names and the match ratios in a single list
    matchRatioList.append({"wrongName": comparedN, "matchedName": referenceN, "ratio": bestRatio, "tokenRatio":bestTokenSetRatio})

if conn:
    conn.close()

try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    print "I am connected to database"
except:
    print "I am unable to connect to the database"

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

try:
    cur.execute("""SELECT name, ref from planet_osm_highways_no_links where name is not null""")

except:
    print "I can't SELECT from the table"

rows = cur.fetchall()

# update table with correct names
for row in rows:
    for item in matchRatioList:
        if item["ratio"] != -1:
            wrongName = item["wrongName"]
            matchedName = item["matchedName"]
            ratio = item["ratio"]
            try:
                cur.execute("UPDATE planet_osm_highways_no_links SET name = %s WHERE name = %s", (matchedName, wrongName))
                conn.commit()

            except psycopg2.DatabaseError, e:
                if conn:
                    conn.rollback()
                print 'Error %s' % e
                sys.exit(1)

if conn:
    conn.close()
