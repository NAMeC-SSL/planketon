from math import atan2, cos, sin
import numpy as np
def line_intersection( circle_center, circle_radius, line_point1, line_point2):
    x1, y1 = line_point1
    x2, y2 = line_point2
    x0, y0 = circle_center
    r = circle_radius
    k, b = np.polyfit([x1, x2], [y1, y2], deg=1)
    A = k**2 + 1
    B = 2*k*b - 2*k*y0 - 2*x0
    C = y0**2 - r**2 + x0**2 - 2*b*y0 + b**2
    discriminant = B**2 - 4*A*C
    if discriminant < 0:
        return None
    elif discriminant == 0:
        x = -B / 2 / A
        y = k * x + b
        return (x, y)
    else:
        x1 = (-B + np.sqrt(discriminant)) / 2 / A
        y1 = k * x1 + b
        x2 = (-B - np.sqrt(discriminant)) / 2 / A
        y2 = k * x2 + b
        return ((x1, y1), (x2, y2))

def angleTo( v1, v2):
    v = v1 - v2
    return atan2(-v[1], -v[0])

def ccw( A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

# Return true if line segments AB and CD intersect
def intersect( A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

def rotateVector(v, theta):
    rot = np.array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])   
    return np.dot(rot, v)
