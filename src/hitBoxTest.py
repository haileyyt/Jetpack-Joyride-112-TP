from PIL import Image
import os, math

# the only function you need to know how to use on this whole file
# is on line ~204 it has a bunch of parameters

def absPath(filename):
    baseDir = os.path.dirname(os.path.abspath(__file__))
    relativePath = os.path.join('Images', filename)
    return os.path.normpath(os.path.join(baseDir, relativePath))

# sources for tracing polygon around image
# https://blog.roboflow.com/edge-detection/
# https://sbme-tutorials.github.io/2018/cv/notes/4_week4.html
def getEdges(image):
    # convert the image to RGBA format
    img = Image.open(absPath(image)).convert('RGBA')
    width, height = img.size
    # get 1d list of pixels
    pixels = list(img.getdata())
    # get 2d list of 1/0s according to not bg
    nonBGPixelList = getNonBGPixels(pixels, width, height)
    # define smth called Laplacian kernel
    # will basically check for edges
    kernel = [[1, 1, 1], [1, -8, 1], [1, 1, 1]]
    # apply kernel to image
    possibleEdges = applyConvolution(nonBGPixelList, kernel)
    edgeList = realEdges(possibleEdges)
    return edgeList

def getNonBGPixels(pixels, width, height):
    result = []
    for i in range(height):
        row = []
        for j in range(width):
            # grab alpha value, alpha > 0 <=> not transparent
            # if not transparent put 1 else 0
            bin = 1 if pixels[i*width + j][3] > 0 else 0
            row.append(bin)
        result.append(row)
    return result

def applyConvolution(nonBGPixelList, kernel):
    width, height = len(nonBGPixelList[0]), len(nonBGPixelList)
    # basically just add 0s around the list
    # so the kernel doesnt slide off
    # note that this mutates maybe it shouldnt
    wrap(nonBGPixelList, width)
    # initialize output
    output = [[0 for i in range(width)] for j in range(height)]
    # now apply kernel to every 3x3 in nonBGPixelList
    for i in range(1, height + 1, 5):
        for j in range(1, width + 1, 5):
            # get 3x3 matrix to apply kernel to
            matrix = getMatrix(nonBGPixelList, i, j)
            # multiply pointwise to get value
            value = mult(matrix, kernel)
            output[i-1][j-1] = value
    return output

# this function mutates
def wrap(L, width):
    for row in L:
        row.insert(0, 0)
        row.append(0)
    L.insert(0, [0 for i in range(width + 2)])
    L.append([0 for i in range(width + 2)])

def getMatrix(L, i, j):
    result = []
    # top row
    result.append(list(L[i-1][j-1:j+2]))
    # middle row
    result.append(list(L[i][j-1:j+2]))
    # bottom row
    result.append(list(L[i+1][j-1:j+2]))
    return result

def mult(matrix, kernel):
    total = 0
    for i in range(3):
        for j in range(3):
            total += matrix[i][j] * kernel[i][j]
    return total

def realEdges(L):
    width, height = len(L[0]), len(L)
    result = []
    for i in range(height):
        for j in range(width):
            #if (i + j) % 10 == 0:
            if L[i][j] > 0:
                result.append((j, i))
    return result

#######above is for polygon tracing, below for convex hull#####
# writing MergeSort using custom comparison function
# https://www.cs.cmu.edu/~112/notes/notes-efficiency.html#sorting
def dist(p0, p1):
    return ((p0[0]-p1[0]) ** 2 + (p0[1]-p1[1]) ** 2) ** 0.5

def customCompare(p0, p1, origin): # want p1 to be below
    o = orientation(origin, p0, p1)
    # if they are colinear say the farther one is "bigger"
    if o == 0:
        return dist(p0, origin) > dist(p1, origin)
    # if they are clockwise p1 is "smaller"
    else:
        return o == 1

def merge(L, start1, start2, end, origin):
    index1 = start1
    index2 = start2
    length = end - start1
    temp = [None] * length
    for i in range(length):
        if ((index1 == start2) or
            ((index2 != end) and 
             (customCompare(L[index1], L[index2], origin)))):
            temp[i] = L[index2]
            index2 += 1
        else:
            temp[i] = L[index1]
            index1 += 1
    for i in range(start1, end):
        L[i] = temp[i - start1]

def customMergeSort(L, origin):
    n = len(L)
    step = 1
    while (step < n):
        for start1 in range(0, n, 2 * step):
            start2 = min(start1 + step, n)
            end = min(start1 + 2*step, n)
            merge(L, start1, start2, end, origin)
        step *= 2
        
##############################################################
# how to get convex hull
# https://www.geeksforgeeks.org/convex-hull-algorithm/
# we want the bottom left most point to orient the other points around
def getBottomLeftMostPoint(pixelList):
    x, y = pixelList[0]
    for x1, y1 in pixelList:
        if x >= x1 or y <= y1:
            x, y = x1, y1
    return (x, y)

# given three points how are they positioned?
# colinear, counterclockwise, clockwise
# https://www.geeksforgeeks.org/orientation-3-ordered-points/
def orientation(p1, p2, p3):
    # compute cross product of vectors p1->p2, p2->p3
    cross = (p2[1]-p1[1])*(p3[0]-p2[0]) - (p2[0]-p1[0])*(p3[1]-p2[1])
    # analyze cross product to determine orientation
    if cross == 0:
        return 0 # let this represent colinear
    elif cross > 0:
        return -1 # let this be counterclockwise
    else:
        return 1 # let this be clockwise
    
# we want to remove the points which cause 
# the polygon to be concave
def filter(start, sortedList):
    # do the first point manually
    # cuz its too much work with loop
    prev = start
    curr = sortedList[0]
    nexst = sortedList[1]
    if orientation(prev, curr, nexst) != -1:
        sortedList.pop(0)
    # go through rest of list
    i = 1
    while len(sortedList) >= 3 and i < len(sortedList) - 1:
        prev = sortedList[i-1]
        curr = sortedList[i]
        nexst = sortedList[i+1]
        # if the orientation is not counterclockwise
        # it is making polygon concave so remove it
        if orientation(prev, curr, nexst) != -1:
            sortedList.pop(i)
            if i != 1:
                i -= 1
        else:
            i += 1

# algorithm for getting convex hull from points
def grahamScan(pixelList):
    start = getBottomLeftMostPoint(pixelList)
    # we add this back at the end
    # so it doesnt get sorted into wrong place
    pixelList.remove(start)
    # sort the list according to angle/slope it makes with start
    customMergeSort(pixelList, start)
    # now remove points that make polygon concave
    filter(start, pixelList)
    return [start] + pixelList

# temp = getEdges("Zapper1.png")
# customMergeSort(temp, getBottomLeftMostPoint(temp))
# gTest = grahamScan(getEdges("Zapper1.png"))
# print(len(temp) == len(gTest))
# # print(getEdges("Zapper1.png"))

#################singular function you can run#################################
# image should be in the form "blahblah.png" or whatever
# topLeft is a tuple
# pass in degrees for theta
# newWidth, newHeight are the desired dimensions of image
def getConvexHull(image, topLeft, newWidth, newHeight, theta):
    img = Image.open(absPath(image))
    oldWidth, oldHeight = img.size
    # get convex hull
    pointList = grahamScan(getEdges(image))
    # compute constants
    dx, dy = topLeft
    factorX, factorY = newWidth / oldWidth, newHeight / oldHeight
    cx, cy = topLeft[0] + newWidth/2, topLeft[1] + newHeight/2
    thetaInRads = math.radians(theta)
    for i in range(len(pointList)):
        x0, y0 = pointList[i]
        # scale point
        x1, y1 = x0 * factorX, y0 * factorY
        # adjust for where topLeft is
        x2, y2 = x1 + dx, y1 + dy
        # apply rotation matrix relative to image center
        vecX, vecY = x2 - cx, y2 - cy
        vecX1 = vecX * math.cos(thetaInRads) - vecY * math.sin(thetaInRads)
        vecY1 = vecX * math.sin(thetaInRads) + vecY * math.cos(thetaInRads)
        x3, y3 = cx + vecX1, cy + vecY1
        pointList[i] = (x3, y3)
    return pointList

def fancyFlattenEdgeList(L):
    result = []
    for i in range(len(L)):
        result.append(L[i][0])
        result.append(L[i][1])
    return result

# def onAppStart(app):
#     app.width = 800
#     app.height = 600
#     app.image = "Coin-135.png"
#     app.topLeft = (100, 100)
#     # this also adjusts for top left of image
#     app.hitbox = fancyFlattenEdgeList(getConvexHull(app.image, 
#                                       app.topLeft, 100, 100, 45))
#     # temp = getEdges("Zapper1.png")
#     # customMergeSort(temp, getBottomLeftMostPoint(temp))
#     # app.hitbox = fancyFlattenEdgeList(temp, app.topLeft[0], app.topLeft[1])

# def redrawAll(app):
#     drawImage(absPath(app.image), app.topLeft[0], app.topLeft[1], 
#               width = 100, height = 100, rotateAngle = 45)
#     drawPolygon(*app.hitbox, fill = None, border = 'black')
#     for i in range(0, len(app.hitbox), 2):
#       drawLabel(f'{i//2}', app.hitbox[i], 
#                 app.hitbox[i+1], size = 15, fill = 'red')

# runApp()