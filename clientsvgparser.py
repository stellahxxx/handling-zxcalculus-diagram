import numpy as np
import xml.etree.ElementTree as ET
import element as elm



def loadFile(filename):  
    """"Load an SVG file. 
    
    Args:
        filename (str): The string of the file name.
    
    Returns:
        The XML tree of the SVG file. 
    
    """
    # Register the name space
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    ET.register_namespace('dc',"http://purl.org/dc/elements/1.1/")
    ET.register_namespace('cc',"http://creativecommons.org/ns#")
    ET.register_namespace('rdf',"http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    ET.register_namespace('svg',"http://www.w3.org/2000/svg")
    ET.register_namespace('sodipodi',"http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd")
    ET.register_namespace('inkscape',"http://www.inkscape.org/namespaces/inkscape")
    tree = ET.parse(filename)
    return tree

    
def parseStroke(stroke_str):
  """
  Parse a path string into a list of points
  Use string 'teststroke_str' as an example: pointlist = paseStroke(teststroke_str)
  """
  points = stroke_str.split('L')
  p1str = points[0].split('M')[1]
  p1 = map(float,p1str.split(','))
  pointlist = [p1]
  rest = map(lambda item:map(float,item.split(',')),points[1:])
  pointlist.extend(rest)
  return pointlist    

def dist(pos1,pos2):
    """Calculate the eucliean distance between two positions.
  
    Args:
        pos1 (list): A list of two float numbers.
        pos2 (list): A list of two float numbers.   
  
    Returns:
        The value of the distance. 
    """
    return np.linalg.norm(np.array(pos1,dtype=np.float32)-np.array(pos2,dtype=np.float32))

    
def getPath(tree): 
    """Load all the paths in one XML tree.
    
    Args:
        tree (obj): An XML tree.
    
    Returns:
        Yield path objects.    
    """
    root = tree.getroot()
    for stroke in root.iter("{http://www.w3.org/2000/svg}path"):
        stroke_str = stroke.attrib["d"]  # the path command has the attribute name "d"
        pointlist = parseStroke(stroke_str)  
        newpath = elm.path(pointlist)
        yield newpath    
  
    
def loadPaths(tree):
    """Create a pathlist containing paths from a XML tree.
    
    Args:
        tree (obj): An XML tree.

    Returns:
        A list of path objects.
    """
    pathlist = []
    for path in getPath(tree):
        pathlist.append(path)
    return pathlist
    
def addStroke(tree,newpath):
    """Draw a stroke on the XML tree. A function for testing. 
    
    Args:
        tree (obj): An XML tree.
        newpath (obj): The path to be added.     
    """
    root = tree.getroot()
    for pathaddr in root.iter('{http://www.w3.org/2000/svg}g'):
        stroke = ET.SubElement(pathaddr,'{http://www.w3.org/2000/svg}path')  
        stroke.attrib['style'] = newpath.style
        stroke.attrib['d'] = newpath.pointStr()
        stroke.attrib['id'] = 'path'+str('1')
        stroke.attrib['inkscape:connector-curvature'] = '0'
        stroke.tail = '\n' 

def addPoint(tree,point,pointtype='c'):
    """Draw a point on the XML tree. A function for testing. 
    
    Args:
        tree (obj): An XML tree.
        newpath (obj): The path to be added.
        pointtype (str): The string of point type. 
    """
    x_str,y_str = str(point[0]),str(point[1])
    root = tree.getroot()
    for pointaddr in root.iter('{http://www.w3.org/2000/svg}g'):
        point = ET.SubElement(pointaddr,'{http://www.w3.org/2000/svg}circle')
        # Offer two colour choice
        if pointtype == 'c':
            point.attrib['style'] = 'fill: #0000ff'
        else:
            point.attrib['style'] = 'fill: #FF0000'
        point.attrib['cx'] = x_str
        point.attrib['cy'] = y_str
        point.attrib['r'] = '0.5'
        point.tail = '\n'

def addDot(tree,dot,colour='red',radius=10.0):
    """Draw a dot on the XML tree.
    
    Args:
        tree (obj): An XML tree.
        dot (obj): The dot to be added.
        colour (str): The string of dot colour. 
        radius (float): The radius of the dot to be drawn on the canvas.
    """
    centre = dot.centre
    x_str,y_str = str(centre[0]),str(centre[1])
    r_str = str(radius)
    root = tree.getroot()
    for pointaddr in root.iter('{http://www.w3.org/2000/svg}g'):
        point = ET.SubElement(pointaddr,'{http://www.w3.org/2000/svg}circle')
        if colour == 'red':
            point.attrib['style'] = 'fill: #FF0000'  # Red
        else:
            point.attrib['style'] = 'fill: ##00ff00'  # Green
        point.attrib['cx'] = x_str
        point.attrib['cy'] = y_str
        point.attrib['r'] = r_str
        point.tail = '\n'

def addMorphism(tree,morphism,a=30,b=40,h=20):
    """Draw a morphism box on the XML tree.
    
    Use M, h, v and z command to draw a morphism. M = moveto(M X,Y), h = horizontal lineto(h X), v = vertical lineto(v Y),
    z = closepath(). h and v command use the relative positions.
    
    Args:
        tree (obj): An XML tree.
        morphism (obj): The morphism to be added. 
        a (float): Length of the top edge.
        b (float): Length of the bottom edge.
        h (float): Length of the left edge.
    """
    centre = morphism.centre
    orient = morphism.orient
    root = tree.getroot()
    
    for pathaddr in root.iter('{http://www.w3.org/2000/svg}g'):
        stroke = ET.SubElement(pathaddr,'{http://www.w3.org/2000/svg}path')  
        stroke.attrib['style'] = "fill:none;stroke:#000000;stroke-width:0.26458332px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
        if orient == "origin":
            corner_str = str(centre[0]+a/2) + ',' + str(centre[1]-h/2)
            stroke.attrib['d'] =  'M ' + corner_str + ' h -' + str(a) + ' v ' + str(h) + ' h ' + str(b) + ' z' 
        elif orient == "hflip":
            corner_str = str(centre[0]-a/2) + ',' + str(centre[1]-h/2)
            stroke.attrib['d'] =  'M ' + corner_str + ' h ' + str(a) + ' v ' + str(h) + ' h -' + str(b) + ' z'  
        elif orient == "hvflip":
            corner_str = str(centre[0]-a/2) + ',' + str(centre[1]+h/2)
            stroke.attrib['d'] =  'M ' + corner_str + ' h ' + str(a) + ' v -' + str(h) + ' h -' + str(b) + ' z'   
        elif orient == "vflip":
            corner_str = str(centre[0]+a/2) + ',' + str(centre[1]+h/2)
            stroke.attrib['d'] =  'M ' + corner_str + ' h -' + str(a) + ' v -' + str(h) + ' h ' + str(b) + ' z'         
        stroke.attrib['id'] = 'path'+str('1')
        stroke.attrib['inkscape:connector-curvature'] = '0'
        stroke.tail = '\n' 

        
def addWire(tree,wire,dot_r=10,mor_h=20):
    """Draw a wire on the XML tree.
    
    First check whether the wire is connected to any dots or morphisms. If yes, change the end point positions and make it 
    on the node boundary. The new end point position has the same angle to the node centroid as the old one.
    
    Args:
        tree (obj): An XML tree.
        wire (obj): The wire to be added. 
        dot_r (float): The radius of the dots.
        mor_h (float): The height of the morphisms.
    """
    points = wire.refinePoints(6)
    if len(wire.connections)!=0:
        for [node,angle,i,_] in wire.connections:
            if node.getType()=='dot':
                # i is 0 or 1,
                # wire.ends[i] corresponds to the two end points in the end list;
                # points[-i] corresponds to the two end points in the points list.
                d = np.array(angle * dot_r / dist(node.centre,wire.ends[i]))  # Use the equation of similar triangles.
                points[-i] = np.array(node.centre)-d
            else:  # nodetype = morphism
                h = mor_h/2
                [x,y] = angle
                d_y = y/abs(y)*h  # Use the equation of similar triangles.
                d_x = d_y*x/y
                points[-i] = [node.centre[0]-d_x,node.centre[1]-d_y]
    root = tree.getroot()
    start_str = 'm '+str(points[0][0])+','+str(points[0][1])
    curve_str = ' C'  # The capital C means absolute positions.
    for point in points[1:]:
        curve_str = curve_str + ' ' +str(point[0])+','+str(point[1])
    path_str = start_str + curve_str
    for pathaddr in root.iter('{http://www.w3.org/2000/svg}g'):
        stroke = ET.SubElement(pathaddr,'{http://www.w3.org/2000/svg}path')  
        stroke.attrib['style'] = "fill:none;stroke:#000000;stroke-width:0.26458332px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
        stroke.attrib['d'] = path_str
        stroke.attrib['id'] = 'path'+str('1')
        stroke.attrib['inkscape:connector-curvature'] = '0'
        stroke.tail = '\n'

        
def transtoInkscapePath(pointlist):
    """Transform absolute positions to relative positions. Used in dataset generation.
    
    Args:
        pointlist (list): A list of points with absolute positions.

    Returns:
        A list of points with relative positions.    
    """
    listlen = len(pointlist)
    i = 0
    interpoint = pointlist[0]
    # Each cubic Bezier Curve has 4 points. The end of the current curve becomes the start of the next curve.
    # In the pointlist each 3 points can generate a new curve. 
    while i<(listlen-3):  
        nextinterpoint = pointlist[i+3]
        pointlist[i+1] = [pointlist[i+1][0]-interpoint[0],pointlist[i+1][1]-interpoint[1]]
        pointlist[i+2] = [pointlist[i+2][0]-interpoint[0],pointlist[i+2][1]-interpoint[1]]
        pointlist[i+3] = [pointlist[i+3][0]-interpoint[0],pointlist[i+3][1]-interpoint[1]]
        interpoint = nextinterpoint  # Update the interpoint. 
        i = i + 3
    return pointlist    
    
    
def writeFile(tree,newname):
    """Write the XML tree to an SVG file.
    
    Args:
        tree (obj): An XML tree.
        newname (str): The name of the new created file. 
    """
    root = tree.getroot()
    root.attrib['{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}docname'] = newname
    tree.write(newname, xml_declaration=True, default_namespace='')


