# -*- coding: utf-8 -*-
"""
Created on Sun Jun 04 17:24:34 2017

@author: Administrator
"""

import math
import numpy as np
from shapely import geometry as geo
import svgparser as sp


class curve:
    """Cubic Bezier Curve.
    
    Curve is the basic unit of the path in SVG. Store the two 
    end points and two control points.

    Attributes:
        start (list): The start point of the bezier curve
        control1 (list): The first control point of the bezier curve
        control2 (list): The second control point of the bezier curve
        end (list): The end point of the bezier curve

    Args:
        start (list): A list including two float numbers
        control1 (list): A list including two float numbers
        control2 (list): A list including two float numbers
        end (list): A list including two float numbers
    """

    def __init__(self, start, control1, control2, end):
        self.start = start
        self.control1 = control1
        self.control2 = control2
        self.end = end

    def pointlist(self):
        """Return a list of the four points. """
        pointlist = [self.start, self.control1, self.control2, self.end]
        return pointlist


class path:
    """A path comprised of Cubic Bezier Curves,
    
    A Path describes one freehand stroke in the SVG. Only command
    M - move to, and C - cubic bezier curve are used.
    A path consists of one M command and 3n C command.  

    Attributes:
        ori_pointlist (list): The list of original path points using relative
                       position
        curves (list): The list of extracted Cubic Bezier Curves
        pointlist (list):  The list of transformed path points using absolute
                    position
        end1 (list): The start point of the pointlist
        end2 (list): The end point of the pointlist
        style (str): The string describing the stroke style in SVG
        linestring (obj): The LineString instance of the pointlist

    Args:
        ori_pointlist (list): A list of points with relative positions.
    """

    def __init__(self, ori_pointlist):
        self.ori_pointlist = ori_pointlist
        self.getCurve()
        self.getPointlist()
        self.getEnds()
        self.style = "fill:none;stroke:#000000;stroke-width:0.26458332px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"

    def getCurve(self):
        """Get the Cubic Bezier Curves of the path.

        Transform relative positions to absolute positions and store every four points in a Curve instance.
        Create a list of curvs.

        """
        self.curves = []
        listlen = len(self.ori_pointlist)
        i = 0
        interpoint = self.ori_pointlist[0]  # the end point of the previous is the start point of the current
        while i < (listlen - 3):
            start = interpoint
            control1 = [start[0] + self.ori_pointlist[i + 1][0], start[1] + self.ori_pointlist[i + 1][1]]
            control2 = [start[0] + self.ori_pointlist[i + 2][0], start[1] + self.ori_pointlist[i + 2][1]]
            end = [start[0] + self.ori_pointlist[i + 3][0], start[1] + self.ori_pointlist[i + 3][1]]
            interpoint = end
            newcurve = curve(start, control1, control2, end)
            self.curves.append(newcurve)
            i = i + 3

    def getPointlist(self):
        """Create a list of points with absolute positions and create a LineString instance. """
        self.pointlist = []
        for curve in self.curves:
            self.pointlist.append(curve.start)
            self.pointlist.append(curve.control1)
            self.pointlist.append(curve.control2)
            self.pointlist.append(curve.end)
        self.linestring = geo.LineString(self.pointlist)

    def getEnds(self):
        """ Set the end points of the path. """
        self.end1 = self.pointlist[0]
        self.end2 = self.pointlist[-1]

    def pointStr(self):
        """Transform the original pointlist to a string which could be used as a command in SVG.

        Returns:
            A string of original points.

        """
        pointstr = ['m', ','.join(list(map(str, self.ori_pointlist[0]))), 'c']
        pointstr.extend(list(map(lambda item: ','.join(list(map(str, item))), self.ori_pointlist[1:])))
        return ' '.join(pointstr)

    def checkIntersect(self, pathlist):
        """Check whether the path intersects with any path in a pathlist.

        If there are more than one intersected paths, the path
        with most intersections will be chosen.

        Args:
            pathlsit (list): A list of path objects.

        Returns:
            A list including a path object and the int number of intersections with this path.

        """
        maxintersect = 0
        replacedpath = None
        for i, path in enumerate(pathlist):
            try:  # If only one intersection it returns a point instance which cannot be counted
                intersect = len(self.linestring.intersection(path.linestring))
            except:
                intersect = 1
            if intersect > maxintersect:
                maxintersect = intersect
                replacedpath = path
        return [replacedpath, maxintersect]


class shape:
    """A shape for classifying.

    A shape is formed by points with absolute positions. It is transformed to a polygon object
    and it contains polygon attributes. These attributes are then used as inputs for the shape classifier.

    Attributes:
        pointlist (list): The list of points of vertex positions.
        poly (obj): The polygon object formed by vertex positions.
        end1 (list): The position of the first vertex.
        end2 (list) : The position of the final vertex.
        boundpos (list): The indexes of boundary vertexes in the boundpoints.
        boundpoints (list): The list of boundary vertexes.
        xbound (list): The boundary position in x axis of the polygon.
        ybound (list): The boundary position in y axis of the polygon.
        area (float): The area of the polygon.
        perim (float): The perimeter of the polygon.
        centroid (list): The centroid position of the polygon.
        attributes (list): Other attributes of the polygon including compactness,
                           eccentricity, rectangularity and circularity


    Args:
        pointlist (list): A list of points with absolute positions.
    """

    def __init__(self, pointlist):
        self.pointlist = pointlist
        self.transPolygon()
        self.getEnds()
        self.getBound()
        self.getAttributes()

    def transPolygon(self):
        """Form the polygon with the pointlist and set two basic attributes: area and perimeter. """
        self.poly = geo.Polygon(self.pointlist)
        self.area = self.poly.area
        self.perim = self.poly.length

    def getEnds(self):
        """ Set the end points of the path. """
        self.end1 = self.pointlist[0]
        self.end2 = self.pointlist[-1]

    def getBound(self):
        """ Set the boundaries of the path. """
        maxpos = np.argmax(self.pointlist, axis=0)
        minpos = np.argmin(self.pointlist, axis=0)
        self.boundpos = np.concatenate((maxpos, minpos))
        self.boundpoints = [self.pointlist[i] for i in self.boundpos]
        [maxx, maxy] = np.max(self.boundpoints, axis=0)
        [minx, miny] = np.min(self.boundpoints, axis=0)
        self.xbound = [minx, maxx]
        self.ybound = [miny, maxy]

    def getAttributes(self):
        """Calculate attributes of the polygon.

        Select four essential attributes used for classify dot and trapezoid: compactness, eccentricity,
        rectangularity and circularity. Store these attributes in a list.

        """
        self.centroid = [self.poly.centroid.x, self.poly.centroid.y]
        compact = 2 * math.sqrt(self.area * math.pi) / self.perim
        eccent = self.eccentricity()
        rectang = self.rectangularity()
        circular = self.circularity()
        aspect = self.aspectRatio()
        #self.attributes = [eccent,circular]
        self.attributes = [eccent,circular,aspect]

    def eccentricity(self):
        """Calculate the eccentricity of the polygon.

        Eccentricity is the ratio of length of major axis to minor axis.

        Returns:
            A float value range from 0 to 1.
        """
        dist = np.matrix(self.pointlist) - np.matrix(self.centroid)
        cov = sum(list(map(lambda x: x.T * x, dist)))
        cxx, cxy, cyx, cyy = cov.item(0), cov.item(1), cov.item(2), cov.item(3)
        b = math.sqrt((cxx + cyy) ** 2 - 4 * (cxx * cyy - cxy ** 2))
        e1 = cxx + cyy + b
        e2 = cxx + cyy - b
        return e2 / e1

    def rectangularity(self):
        """Calculate the rectangularity of the polygon.

        Rectangularity equals (polygon area)/(boundary area). It demonstrates how square
        the polygon is.

        Returns:
            A float value range from 0 to 1.
        """
        boundarea = (self.xbound[1] - self.xbound[0]) * (self.ybound[1] - self.ybound[0])
        return self.area / boundarea

    def circularity(self):
        """Calculate the circularity of the polygon.

        Calculate the distance between the farthest vertex and the centroid, and use the distance as
        the radius of a circle. Circularity equals (polygon area)/(circle area). It decomstrates how circle the
        polygon is.

        Returns:
            A float value range from 0 to 1.
        """
        sub = np.array(self.boundpoints, dtype=np.float32) - np.array(self.centroid, dtype=np.float32)
        ecldndist = list(map(lambda x: np.linalg.norm(x), sub))
        r = max(ecldndist)
        circlearea = math.pi * r ** 2
        return self.area / circlearea
    def aspectRatio(self):
        return (self.xbound[1] - self.xbound[0])/(self.ybound[1] - self.ybound[0])
    def openCheck(self, threshold=0.10):
        """Check whether the polygon is a closed shape.

        Calculate the distance between the two ends of the polygon. If the ratio between the distance and the polygon
        perimeter is over a threshold, the polygon is considered an open shape.

        Args:
            threshold (float): The threshold number of the ratio.

        Returns:
            True if the polygon is open. False otherwise.
        """
        dist = np.linalg.norm(np.array(self.end1, dtype=np.float32) - np.array(self.end2, dtype=np.float32))
        ratio = dist / self.perim
        if ratio > threshold:
            return True
        else:
            return False

    def convexCheck(self, threshold=1.30):
        """Check whether the polygon is a convex shape.

        Calculate the area of the convex hull of the polygon. If the ratio between the convex hull area and the polygon
        area is over some threshold, the polygon is considered a concave shape.

        Args:
            threshold (float): The threshold number of the ratio.

        Returns:
            True if the polygon is a convex shape. False if it is concave.
        """
        convexhull = self.poly.convex_hull
        ch_area = convexhull.area
        ratio = ch_area / self.area
        if ratio > threshold:
            return True
        else:
            return False

    def orientation(self):
        """Calculate the orientation of the polygon.

        This is a function for morphism nodes. Calculate the distance between the farthest vertex and the centroid.
        Divide the coordinate into 8 parts by x axis, y axis and two diagonals and use these 8 direction as the
        morphism orientation.

        Returns:
            An int range from 0 to 7.
        """
        distances = [sp.dist(self.centroid, boundpoint) for boundpoint in self.boundpoints]
        cornerpoint = self.boundpoints[np.argmax(distances)]
        [dx, dy] = np.array(self.centroid) - np.array(cornerpoint)
        if dx < 0 and dy < 0:
            return 'origin'
        elif dx >= 0 and dy < 0:
            return 'hflip'
        elif dx > 0 and dy > 0:
            return 'hvflip'
        else:
            return 'vflip'


class dot():
    """The class of dot nodes.

    A shape classified as a dot node. Dot objects will be then used in connection.

    Attributes:
        centre (list): The centre position of the dots.
        poly (obj): The original polygon object formed by vertex positions.
        pointlist (list): The list of polygon vertex points.
        connection (int): The number of connected wires of this node.

    Args:
        centre (list): A list of two float numbers.
        poly (obj): An polygon obejct.
        pointlist (list): A list of points with absolute positions.
    """
    def __init__(self, centre, poly, pointlist):
        self.centre = centre
        self.poly = poly
        self.pointlist = pointlist
        self.connections = []
        self.relative_pos = [0,0]
        self.colour = ""

    def getType(self):
        """Return the name of the node type. """
        return 'dot'

    def addConnection(self,connection):
        """Increase the number of connection by 1 once called."""
        self.connections.append(connection)

    def setRelativePos(self,pos):
        """Set the relative position as an attributs of the wire.
        
        Args:
            pos (list): The relative position.
        """
        self.relative_pos = pos
       
    def giveId(self,i):
        """Give the node an id.
        
        Args:
            i (int): The id of the node
        
        """
        self.node_id = i
        self.func_name = ""
        
    def getOrientStr(self):
        """Get the string of the node's orientation.
        
        Returns:
            A string of the orientation.
        """
        return ""
       
        
class morphism():
    """The class of morphism nodes.

    A shape classified as a morphism node. Morphism objects will be then used in connection.

    Attributes:
        centre (list): The centre position of the morphism.
        poly (obj): The original polygon object formed by vertex positions.
        pointlist (list): The list of polygon vertex points.
        orient (int): The orientation of the morphism.
        connection (int): The number of connected wires of this node.

    Args:
        centre (list): A list of two float numbers.
        poly (obj): An polygon obejct.
        pointlist (list): A list of points with absolute positions.
        orient (int): An int range from 0 to 7.
    """
    def __init__(self, centre, poly, pointlist, orient):
        self.centre = centre
        self.poly = poly
        self.pointlist = pointlist
        self.connections = []
        self.colour = ""
        self.orient = orient

    def getType(self):
        """Return the name of the node type. """
        return 'morphism'

    def addConnection(self,connection):
        """Increase the number of connection by 1 once called."""
        self.connections.append(connection)
        
    def sortConnection(self):
        """Sort the connections list according to the x value of the angle.
        """
        self.connections = sorted(self.connections, key=lambda connection: connection[1][0], reverse=True)

    def setRelativePos(self,pos):
        """Set the relative position as an attributs of the wire.
        
        Args:
            pos (list): The relative position.
        """        
        self.relative_pos = pos

    def giveId(self,i):
        """Give the node an id and a function name.
        
        Args:
            i (int): The id of the node
        """
        self.node_id = i
        self.func_name = "$$"
        
    def getOrientStr(self):
        """Get the string of the node's orientation.
        
        Returns:
            A string of the orientation.
        """
        if self.orient == "origin":
            return ""
        else:
            return ","+self.orient
        
class wire():
    """The class of wires.

    A shape classified as a wire. Wire objects will be then used in connection.

    Attributes:
        ends (list): A list of two end points' positions.
        pointlist (list): The list of polygon vertex points.
        connection (list): The connection information of the wire.

    Args:
        ends (list): A list of two point positions.
        pointlist (list): A list of points with absolute positions.
    """
    def __init__(self, ends, pointlist):
        self.ends = ends
        self.pointlist = pointlist
        self.connections = []
        self.shifts = []

    def calculateAngle(self, end, centre):
        """Calculate the angle of the wire end and the node centre.

        Returns:
            A list of two flaot numbers.
        """
        return np.array(centre) - np.array(end)

    def connect(self, nodelist, threshold=15.0):
        """ Connect the wire with nodes.

        For each end of the wire, check the distance between the end position and every node's vertex position.
        If the distance is under some threshold, consider this node is a neighbour and store it in a list. After
        checking with all the nodes in the nodelist, choose the node with least distance as the connection of this
        end. Finally in the connection attribute, each element will contain the connected node, the angle between
        the node and the end, and which end fo the wire this connection belongs to.

        Args:
            nodelist (list): A list of node objects including dots and morphisms,
            threshold (float): The threshold value of distance.

        Raise:
            Exception: The neighbour list could be blank if the wire doesn't connect with any nodes.
        """
        for i, end in enumerate(self.ends):
            neighbours = []
            for node in nodelist:
                distlist = [sp.dist(end, point) for point in node.pointlist]
                mindist = min(distlist)
                if mindist < threshold:
                    neighbours.append([node, mindist])
            try:
                mindist_idx = np.argmin(neighbours, axis=0)[1]  # The index of the min distance in the neighbours list.
                connectnode = neighbours[mindist_idx][0]
                angle = self.calculateAngle(end, connectnode.centre)
                self.connections.append([connectnode, angle, i, 0])
                yield [connectnode, angle, i, 0]
            except:
                pass

    def refinePoints(self, pnumber=3):
        """Reduce the number of points in the pointlist.

        This function is used for drawing the outputs. It enables the SVG to draw smooth or straight wires.

        Args:
            pnumber (int): The final point number of the wire will be pnumber+1. The pnumber must be set at
                           3n like 3, 6, 9 because a path contains 3n+1 points.
        Returns:
            refinedpoints (list): The refined pointlist.
        """
        listlen = len(self.pointlist)
        if listlen > pnumber:
            interval = listlen / float(pnumber)
            pointpos = map(lambda x: int(x * interval), range(pnumber))
            refinedpoints = [self.pointlist[i] for i in pointpos]
            refinedpoints.append(self.pointlist[-1])
        else:  # If the original point number is smaller than pnumber, than use the original one.
            refinedpoints = self.pointlist
        return refinedpoints
        
    def getLength(self):
        """Calculate the length of the wire.
        
        Returns:
            The float value of the length.
        
        """
        linestring = geo.LineString(self.pointlist)
        return linestring.length
    
    def changeShift(self,i,shift):
        """Modify the shift value in the connections attribute.
        
        Args:
            i (int): The id of the end.
            shift (float): The distance of shift.
        """
        for connection in self.connections:
            if connection[2] == i:
                connection[3] = shift