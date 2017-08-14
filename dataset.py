# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 12:05:30 2017

@author: 瑞婷
"""

import random
import math
import element as elm
import svgparser as sp


def randommove(point,r,ratio):
    """Move the point in random direction.

    The movement ranges from 0 to sqrt(2)*r*ratio in random direction.

    Args:
        point (list): A list of two float numbers.
        r (float): The radius of the shape to which the point belongs.
        ratio (float): The movement range ratio.

    Returns:
        A new point after the random movement.
    """
    moverange = r*ratio
    # Transform the random number to make its centre at 0.0.
    xmove = (random.random()-0.5)*2*moverange
    ymove = (random.random()-0.5)*2*moverange
    point = [point[0]+xmove,point[1]+ymove]
    return point


def deform(pointlist,r,ratio):
    """Randomly move every point in the pathlist.

    Args:
        pointlist (list): A list of points.
        r (float): The radius of the shape to which the point belongs.
        ratio (float): The movement range ratio.

    Returns:
        A new pointlist after the random movements.
    """
    pointlist = [randommove(point,r,ratio) for point in pointlist]
    return pointlist


def generateArgs(ranges):
    """Generate random arguments in the range.

    Args:
        ranges (list): A list of ranges. Each range has a lower bound and an upper bound.
                       For example: [[0,100],[5,10]]

    Returns:
        args (list): A list of arguments.
    """
    args = [random.randint(*irange) for irange in ranges]
    return args


def circlepoint(c,r):
    """Generate a point [x,y] lying on a circle by the circle equation.

    Args:
        c (list): The position of circle centre.
        r (float): The radius of the circle.

    Returns:
        A point lies on a circle. The point position is random.
    """
    x = random.uniform(-r,r)  # Randomly find the x position.
    negative = bool(random.getrandbits(1))  # Randomly set whether the point is on the positive y side or negative side.
    y = math.sqrt(r**2-x**2)  # The equation of the circle.
    if negative:
        y = -y
    return [x+c[0],y+c[1]]


def circlepointlist(pointnum,c,r,deformratio):
    """Generate a list of deformed circle points with relative positions in clockwise.

    Args:
        pointnum (int): The number of points in the pointlist.
        c (list): The position of circle centre.
        r (float): The radius of the circle.
        deformratio (float): The ratio of deformation.

    Returns:
        A list of deformed circle points with relative positions in clockwise.
    """
    pointlist = [circlepoint(c,r) for _ in xrange (pointnum)]
    # A circle is divided into two parts according to their y value.
    posy = []
    negy = []
    for point in pointlist:
        if point[1]>c[1]:
            posy.append(point)
        else:
            negy.append(point)
    # Two parts have different sorting rules.
    posy.sort(key=lambda x:x[0])
    negy.sort(key=lambda x:x[0],reverse=True)
    pointlist = posy+negy
    pointlist.append(pointlist[0]) # Make a close circle.
    pointlist = deform(pointlist,r,deformratio)  # Randomly move the points.
    pointlist = sp.transtoInkscapePath(pointlist)  # Transform to relative position.
    return pointlist


def generateDotPath(pointnrange=[80,120],c=[200,200],rrange=[60,80],deformratio=0.03):
    """Generate a path object which has a freehand dot shape.

    The generated path has a random point dense and a random circle size.

     Args:
        pointnrange (list): The range of point numbers.
        c (list): The position of circle centre.
        rrange (list): The range of circle radius.
        deformratio (float): The ratio of deformation.

     Returns:
        A path object.
    """
    [pointnum,r] = generateArgs([pointnrange,rrange])  # Randomly select the arguments.
    pointlist = circlepointlist(pointnum,c,r,deformratio)
    dotpath = elm.path(pointlist)
    return dotpath

def trapezoidpoint(c,a,b,h,edge):
    """Generate a point [x,y] lying on a right trapezoid by the line equations.

    Args:
        c (list): The position of circle centre.
        a (float): The bottom edge length of the trapezoid.
        b (float): The top edge length of the trapezoid.
        h (float): The left edge length of the trapezoid.
        edge (int): Ranges from 0 to 3. Corresponds to the four edges of the trapezoid.

    Returns:
        A point lies on a trapezoid. The point position is random.
    """
    if a>b:
        a,b = b,a  # Make sure a is smaller than b.
    if edge == 0:
        # the top edge
        x = random.uniform(-1,1)*(a/2)
        y = -h/2
    elif edge == 1:
        # the right edge
        y = random.uniform(-1,1)*h/2
        x = (2*b-a)/h * y + b
    elif edge == 2:
        # the bottom edge
        x = random.uniform(-a/2,b-a/2)
        y = h/2
    else:
        # edge==3, the left edge
        x = -a/2
        y = random.uniform(-1,1)*h/2
    point = [x+c[0],y+c[1]]
    return point


def trapezoidpointlist(pointnum,c,a,b,h,deformratio):
    """Generate a list of deformed right trapezoid points with relative positions in clockwise.

    Args:
        pointnum (int): The number of points in the pointlist.
        c (list): The position of circle centre.
        a (float): The bottom edge length of the trapezoid.
        b (float): The top edge length of the trapezoid.
        h (float): The left edge length of the trapezoid.
        deformratio (float): The ratio of deformation.

    Returns:
        A list of deformed circle points with relative positions in clockwise.
    """
    edges = [[] for i in range(4)]
    # Generate a random number from 0 to 3 to decide on which edge is the point.
    edge_i = [random.getrandbits(2) for i in range(pointnum)]
    for i in edge_i:
        point = trapezoidpoint(c,a,b,h,i)
        edges[i].append(point)
    # Sort four edges to make the whole points clockwise.
    edges[0].sort(key=lambda x:x[0])
    edges[1].sort(key=lambda x:x[0])
    edges[2].sort(key=lambda x:x[0],reverse=True)
    edges[3].sort(key=lambda x:x[1],reverse=True)
    pointlist = edges[0]+edges[1]+edges[2]+edges[3]
    pointlist.append(pointlist[0])
    r = math.sqrt((a**2)/4+(b**2)/4)  # The radius is the distance from centre to top-left corner.
    pointlist = deform(pointlist,r,deformratio)
    pointlist = sp.transtoInkscapePath(pointlist)
    return pointlist


def generateMorphismPath(pointnrange=[80,120],c=[200,200],arange=[40,70],brange=[50,90],hrange=[30,80],deformratio=0.025):
    """Generate a path object which has a freehand morphism shape.

    The generated path has a random point dense and a random trapezoid size.

     Args:
        pointnrange (list): The range of point numbers.
        c (list): The position of morphism centre.
        arange (list): The range of the bottom edge length.
        brange (list): The range of the top edge length.
        hrange (list): The range of the left edge length.
        deformratio (float): The ratio of deformation.

     Returns:
        A path object.
    """
    [pointnum,a,b,h] = generateArgs([pointnrange,arange,brange,hrange])  # Generate ramdom arguments.
    pointlist = trapezoidpointlist(pointnum,c,a,b,h,deformratio)
    morphismpath = elm.path(pointlist)
    return morphismpath


def simple_test(nodetype,output_name):
    """A simple test function to generate shapes. The output will appear in the folder.

    Args:
        nodetype (str): 'dot' or 'morphism'.
        output_name (str): The file name of the output image.
    """
    tree = sp.loadFile('datablank.svg')
    if nodetype=='dot':
        path0 = generateDotPath()
    elif nodetype=='morphism':
        path0 = generateMorphismPath()
    else:
        pass
    for point in path0.pointlist:
        sp.addPoint(tree,point)
    tree = sp.addStroke(tree,path0)
    sp.writeFile(tree,output_name)
