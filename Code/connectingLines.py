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
                # try to add here l1[2] and l2[2] - create an object out of point
                # coordinates and line id
                #closePointsWithIDs.append([(l1[i], l1[2]), (l2[j], l2[2])])
                return {"indices": (i, j), "points": (l1[i], l2[j])}
    return NULL

def getNewLine(l1, l2, closePoints):


# Create an array to collect all the close-by points.
# f1[2] < f2[2] check the id, so that only once a single endpoint
# would be compared  (handshakes) - f1[2] is the id.

closeLines = []

for f1 in startEndPoints:
    for f2 in startEndPoints:
        if f1["id"] < f2["id"]:
            closePoints = getClosePointsForLines(f1["line"], f2["line"])
            if closePoints:
                closeLines.append({"original": (f1, f2), "new": getNewLine(f1["line"], f2["line"], closePoints)})

#closeLines = [(f1, f2) for f1 in startEndPoints for f2 in startEndPoints if (f1["id"] < f2["id"]) and linesAreTouchingEachOther(f1["line"], f2["line"])]

#zip(*closeLines)
# Check the first two pairs of points.
closeLines[0]
# If I test this with 1 line pair, it will be out of range
# because there should be only 1 array.
closeLines[1]

newCoordinate = []

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
        newCoordinate.append(p1)
        return True
    return False
'''
# doesn't work further!!!
L = []
L = [newClosePointsCoordinates(closeLines[0][0], closeLines[0][1]) for closeLines[0] in closeLines for closeLines[1] in closeLines]
# Should be list
type(L)
'''
#newCoordinate should be equal to closeLines[0][0] and closeLines[0][1]
