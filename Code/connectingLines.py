from math import sqrt

# Select the active layer.
mylayer = iface.activeLayer()

# List of all start-points and end-points of all line segments and their id
startEndPoints = []

for feature in mylayer.getFeatures():
    xy = feature.geometry().asPolyline()
    startEndPoints.append({"line": (xy[0], xy[-1]), "id": feature.id()})


# Get the paths for SVG drawing
# Start
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
#End

# Radius in which every 2 points are checked
C_TRESHHOLD = 0.001

# Calculate the distance between every 2 points and if they are within the defined radius.
def arePointsCloseToEachOther(p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return sqrt((dx * dx) + (dy * dy)) < C_TRESHHOLD

# Check if lines are touching each other.
def getClosePointsForLines(l1, l2):
    for i in xrange(2):
        for j in xrange(2):
            # start to compare with the last point and then only first point in case input line
            # still has all its points (we need only start and end)
            if arePointsCloseToEachOther(l1[i - 1], l2[j - 1]):
                # Print the close by points (without this line it will print the close by
                # lines). not sure now, maybe it prints close lines
                print (l1[i - 1], l2[j - 1])
                # try to add here l1[2] and l2[2] - create an object out of point,
                # coordinates and line id
                #closePointsWithIDs.append([(l1[i], l1[2]), (l2[j], l2[2])])
                # index 0 means it's the startpoint, index 1 means it's the endpoint
                return {"indices": [i, j], "points": [l1[i], l2[j]]}
    return NULL

#def getNewLine(l1, l2, closePoints):


# Create an array to collect all the close-by points.
# f1[2] < f2[2] check the id, so that only once a single endpoint
# would be compared  (handshakes) - f1[2] is the id.

closeLines = []

'''for f1 in startEndPoints:
    for f2 in startEndPoints:
        if f1["id"] < f2["id"]:
            closePoints = getClosePointsForLines(f1["line"], f2["line"])
            if closePoints:
                closeLines.append({"original": (f1, f2), "new": getNewLine(f1["line"], f2["line"], closePoints)})'''



newLines = []
# cP = close points
def newClosePointsCoordinates(cP, cL):
    # if it is equal, then new coordinate is old coordinate
#if p["ids"][0]!= p["ids"][1] :
    eP = cP["lines"]["points"][0]
    sP = cP["lines"]["points"][1]
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
    cP["lines"]["points"][0] = newCoord
    cP["lines"]["points"][1] = newCoord
    #newCoordinate.append(p1)
    #check for one line to have a changable startingpoint
    if cP["lines"]["indices"][0] == 0 and cL[0]["original"]["id"] == cP["ids"][0]:
        newLines.append({"line":(newCoord, cL[0]["original"]["line"][1]), "id":cP["ids"][0]})
    #check for one line to have a changable startingpoint
    elif cP["lines"]["indices"][1] == 0 and cL[0]["original"]["id"] == cP["ids"][1]:
        newLines.append({"line":(newCoord, cL[0]["original"]["line"][1]), "id":cP["ids"][1]})
    else:
        return False
    return newLines

newLines = []
# cP = close points
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
            # if first point to be changed was a start point of original line and if its id matches id from its original line
            if pointPair["lines"]["indices"][0] == 0 and linePair["original"][0]["id"] == pointPair["ids"][0]:
                # apply new coordinate to the start point, end point stays the same
                newLines.append({"line":(newCoord, linePair["original"][0]["line"][1]), "id":pointPair["ids"][0]})
            # if first point to be changed was an end point of original line and if its id matches id from its original line
            elif pointPair["lines"]["indices"][0] == 1 and linePair["original"][0]["id"] == pointPair["ids"][0]:
                # apply new coordinate to the end point, start point stays the same
                newLines.append({"line":(linePair["original"][0]["line"][0], newCoord), "id":pointPair["ids"][0]})
            else:
                return False
            # if first point to be changed was a start point of original line and if its id matches id from its original line
            if pointPair["lines"]["indices"][1] == 0 and linePair["original"][1]["id"] == pointPair["ids"][1]:
                # apply new coordinate to the start point, end point stays the same
                newLines.append({"line":(newCoord, linePair["original"][1]["line"][1]), "id":pointPair["ids"][1]})
            # if first point to be changed was an end point of original line and if its id matches id from its original line
            elif pointPair["lines"]["indices"][1] == 1 and linePair["original"][1]["id"] == pointPair["ids"][1]:
                # apply new coordinate to the end point, start point stays the same
                newLines.append({"line":(linePair["original"][1]["line"][0], newCoord), "id":pointPair["ids"][1]})
            else:
                return False
    return newLines

testing = []
testing.append({"new": newClosePointsCoordinates(closePoints, closeLines)})


    '''if cP["lines"]["indices"][0] == 0:
        return {"line": (newCoord, (closeLines[-1]["line"][-1] where closeLines["line"]["id"] == cP["ids"][0]), "id": cP["ids"][0]}
    elif cP["lines"]["indices"][0] == 1:
        return {"line": (eP, newCoord), "id": cP["ids"][0]}
    else: False'''
#return False

closePoints = []
for f1 in startEndPoints:
    for f2 in startEndPoints:
        if f1["id"] < f2["id"] and getClosePointsForLines(f1["line"], f2["line"]):
            #closeLines.append([f1, f2])
            closePoints.append({ "lines": getClosePointsForLines(f1["line"], f2["line"]), "ids": [f1["id"], f2["id"]]})
            closeLines.append({"original": [f1, f2]})

for p in closePoints:
    testing = {"new": newClosePointsCoordinates(p, closeLines)}

#closeLines = [(f1, f2) for f1 in startEndPoints for f2 in startEndPoints if (f1["id"] < f2["id"]) and linesAreTouchingEachOther(f1["line"], f2["line"])]

#zip(*closeLines)
# Check the first two pairs of points.
closeLines[0]
# If I test this with 1 line pair, it will be out of range
# because there should be only 1 array.
closeLines[1]


'''
def newClosePointsCoordinates(p1, p2):
    # if it is equal, then new coordinate is old coordinate
    if p1 != p2 :
        eP = p1
        sP = p2
        ePx = p1[0]
        ePy = p1[1]
        sPx = p2[0]
        sPy = p2[1]
        newX = ePx - ((ePx - sPx)/2)
        newY = ePy - ((ePy - sPy)/2)
        # think of a way to say that they all are equal
        ePx = newX
        ePy = newY
        sPx = newX
        sPy = newY
        p1 = (ePx, ePy)
        p2 = (sPx, sPy)
        print (p1, p2)
        #newCoordinate.append(p1)
        return {}
    return False
'''
'''
# doesn't work further!!!
L = []
L = [newClosePointsCoordinates(closeLines[0][0], closeLines[0][1]) for closeLines[0] in closeLines for closeLines[1] in closeLines]
# Should be list
type(L)
'''
#newCoordinate should be equal to closeLines[0][0] and closeLines[0][1]
