from cmu_graphics import *

class Vector:
    def __init__(self, *v):
        self.v = tuple(v)

    def __repr__(self):
        return str(self.v)
    
    #Make it subscriptable
    def __getitem__(self, i):
        return self.v[i]
    
    def __len__(self):
        return len(self.v)
    
    def __mul__(self, c):
        return Vector(*[c*self[i] for i in range(len(self))])
    
    def __add__(self, other):
        return Vector(*[self[i]+other[i] for i in range(len(self))])
    
    def __sub__(self, other):
        return Vector(*[self[i]-other[i] for i in range(len(self))])
    
    #Standard Dot Product 
    def dot(self, w):
        return sum([self[i]*w[i] for i in range(len(self.v))])

    def perp2d(self):
        return Vector(-self[1], self[0])
    
    def proj(self, w):
        scale = self.dot(w) / w.dot(w) #Normalize   
        return w*scale


class HitBox:
    def __init__(self, *polygon):
        self.polygon = polygon

    #Check if Barry touches 
    # note that this is diff than whats in obstacleGeneration
    def check(self, hurtbox): 
        if self.checkCollision(hurtbox):
            self.effect()
    
    #https://en.wikipedia.org/wiki/Hyperplane_separation_theorem
    #Separate Axis Theorem
    #A, B are lists of vertices of polygons in any orientation
    def checkCollision(self, polyB): 
        self.polygon = [Vector(*coord) for coord in self.polygon]
        polyB = [Vector(*coord) for coord in polyB]
        axes1 = getAxes(self.polygon)
        axes2 = getAxes(polyB)

        for axis in axes1 + axes2:
            min1, max1 = project(self.polygon, axis)
            min2, max2 = project(polyB, axis)
            # Found a separating axis
            if not overlap(min1, max1, min2, max2): return False  
        return True
    
    def effect(self): #What happens if Barry touches
        app.gameOver = True

def vectorsBetween(v1, v2):
    direction = v2 - v1
    steps = max(abs(x) for x in direction)
    
    if steps == 0: return Vector(v1)  # Both vectors are equal

    # Normalize to unit step (integer increments)
    step = Vector(*[d // steps for d in direction.v])
    
    return [v1 + step * i for i in range(steps + 1)]

def getAxes(polygon):
    axes = []
    n = len(polygon)
    for i in range(n):
        edge = polygon[(i + 1) % n] - polygon[i]
        normal = edge.perp2d()  # Get perpendicular axis
        axes.append(normal)
    return axes

def project(polygon, axis):
    projections = [point.dot(axis) for point in polygon]
    return min(projections), max(projections)

def overlap(minA, maxA, minB, maxB):
    return maxA >= minB and maxB >= minA