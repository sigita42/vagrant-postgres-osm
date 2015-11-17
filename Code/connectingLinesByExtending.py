from math import sqrt

# Select the active layer.
mylayer = iface.activeLayer()

# List of all start-points and end-points of all line segments and their id
startEndPoints = []

for feature in mylayer.getFeatures():
    xy = feature.geometry().asPolyline()
    startEndPoints.append({"line": (xy[0], xy[-1]), "id": feature.id()})


# Get the paths for SVG drawing
### Start
paths = []

for feature in mylayer.getFeatures():
    if feature.geometry().asMultiPolyline():
        # keep all the points of the line
        paths.extend([{"line": l, "id": features.id()} for l in feature.geometry().asMultiPolyline()])
    elif feature.geometry().asPolyline():
        paths.append({"line": feature.geometry().asPolyline(), "id": features.id()})

svgText = ''
for line in paths:
    svgText += '<polyline points="'
    for point in line:
        svgText += (str(point[0]) + ',' + str(-1 * point[1]) + ' ')
    svgText += '" />'

print svgText
### End

# it should look for the shortest between lines and not stop!!!!!
# Radius in which every 2 points are checked
C_TRESHHOLD = 0.0002

# Calculate the distance between every 2 points and if they are within the defined radius.
# The distance also has to be higher than 0. Otherwise points meet.
def arePointsCloseToEachOther(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return sqrt((dx * dx) + (dy * dy)) < C_TRESHHOLD and sqrt((dx * dx) + (dy * dy)) > 0

# Check if lines are touching each other.
def getClosePointsForLines(l1, l2):
    for i in xrange(2):
        for j in xrange(2):
            # Compare with the last point and then first point, in case input line
            # still has all its points (we need only start and end)
            if arePointsCloseToEachOther(l1[i - 1], l2[j - 1]):
                # Print the close by points
                print (l1[i - 1], l2[j - 1])
                # index 0 means it's the endpoint, index 1 means it's the startpoint!!!!!!!!!!
                return {"indices": [i-1, j-1], "points": [l1[i-1], l2[j-1]]}
    return NULL

# Create a list to collect all the close-by points.
closePoints = []
# Create a list to collect all the close-by lines.
closeLines = []

for f1 in startEndPoints:
    for f2 in startEndPoints:
        # f1[2] < f2[2] check the id, so that only once a single endpoint would be compared  (handshakes).
        if f1["id"] < f2["id"] and getClosePointsForLines(f1["line"], f2["line"]):
            closePoints.append({ "lines": getClosePointsForLines(f1["line"], f2["line"]), "ids": [f1["id"], f2["id"]]})
            closeLines.append({"original": [f1, f2]})

# Lines with the fixed point coordinates
newLines = []
# cP = close points
# cL = close lines
def newClosePointsCoordinates(cP, cL):
    for pointPair in cP:
        eP = pointPair["lines"]["points"][0]
        sP = pointPair["lines"]["points"][1]
        ePx = eP[0]
        ePy = eP[1]
        sPx = sP[0]
        sPy = sP[1]
        newX = ePx - ((ePx - sPx)/2)
        newY = ePy - ((ePy - sPy)/2)
        # think of a way to say that they all are equal
        ePx = newX
        ePy = newY
        sPx = newX
        sPy = newY
        newCoord = (ePx, ePy)
        pointPair["lines"]["points"][0] = newCoord
        pointPair["lines"]["points"][1] = newCoord
        for linePair in cL:
            # if first point to be changed has a start point of original line and if its id matches id from its original line
            if pointPair["lines"]["indices"][0] == -1 and linePair["original"][0]["id"] == pointPair["ids"][0]:
                # apply new coordinate to the start point, end point stays the same
                newLines.append({"line":(linePair["original"][0]["line"][0], newCoord), "id":pointPair["ids"][0]})
            # if first point to be changed was an end point of original line and if its id matches id from its original line
            elif pointPair["lines"]["indices"][0] == 0 and linePair["original"][0]["id"] == pointPair["ids"][0]:
                # apply new coordinate to the end point, start point stays the same
                newLines.append({"line":(newCoord, linePair["original"][0]["line"][-1]), "id":pointPair["ids"][0]})
            else:
                return False
            # if first point to be changed was a start point of original line and if its id matches id from its original line
            if pointPair["lines"]["indices"][1] == -1 and linePair["original"][1]["id"] == pointPair["ids"][1]:
                # apply new coordinate to the start point, end point stays the same
                newLines.append({"line":(linePair["original"][1]["line"][0], newCoord), "id":pointPair["ids"][1]})
            # if first point to be changed was an end point of original line and if its id matches id from its original line
            elif pointPair["lines"]["indices"][1] == 0 and linePair["original"][1]["id"] == pointPair["ids"][1]:
                # apply new coordinate to the end point, start point stays the same
                newLines.append({"line":(newCoord, linePair["original"][1]["line"][-1]), "id":pointPair["ids"][1]})
            else:
                return False
    return newLines

newClosePointsCoordinates(closePoints, closeLines)

#Create the points
# create a memory layer with two points
fixedlines =  QgsVectorLayer('Point', 'points' , "memory")
pr = fixedlines.dataProvider()
# add the first point
pt = QgsFeature()
coordx1 = newLines[0]["line"][0][0]
coordy1 = newLines[0]["line"][0][1]
coordx2 = newLines[0]["line"][1][0]
coordy2 = newLines[0]["line"][1][1]
point1 = QgsPoint(coordx1, coordy1)
pt.setGeometry(QgsGeometry.fromPoint(point1))
pr.addFeatures([pt])
# update extent of the layer
fixedlines.updateExtents()
# add the second point
pt = QgsFeature()
point2 = QgsPoint(coordx2, coordy2)
pt.setGeometry(QgsGeometry.fromPoint(point2))
pr.addFeatures([pt])
# update extent
fixedlines.updateExtents()
# add the layer to the canvas
QgsMapLayerRegistry.instance().addMapLayers([fixedlines])
#Create a new line
fixedlines =  QgsVectorLayer('LineString', 'line' , "memory")
pr = fixedlines.dataProvider()
line = QgsFeature()
line.setGeometry(QgsGeometry.fromPolyline([point1,point2]))
pr.addFeatures([line])
fixedlines.updateExtents()
QgsMapLayerRegistry.instance().addMapLayers([fixedlines])


#Create the points
# create a memory layer with two points
fixedlines2 =  QgsVectorLayer('Point', 'points' , "memory")
pr = fixedlines2.dataProvider()
# add the first point
pt = QgsFeature()
coordx1 = newLines[1]["line"][0][0]
coordy1 = newLines[1]["line"][0][1]
coordx2 = newLines[1]["line"][1][0]
coordy2 = newLines[1]["line"][1][1]
point1 = QgsPoint(coordx1, coordy1)
pt.setGeometry(QgsGeometry.fromPoint(point1))
pr.addFeatures([pt])
# update extent of the layer
fixedlines2.updateExtents()
# add the second point
pt = QgsFeature()
point2 = QgsPoint(coordx2, coordy2)
pt.setGeometry(QgsGeometry.fromPoint(point2))
pr.addFeatures([pt])
# update extent
fixedlines2.updateExtents()
# add the layer to the canvas
QgsMapLayerRegistry.instance().addMapLayers([fixedlines2])
#Create a new line
fixedlines2 =  QgsVectorLayer('LineString', 'line' , "memory")
pr = fixedlines2.dataProvider()
line = QgsFeature()
line.setGeometry(QgsGeometry.fromPolyline([point1,point2]))
pr.addFeatures([line])
fixedlines2.updateExtents()
QgsMapLayerRegistry.instance().addMapLayers([fixedlines2])

