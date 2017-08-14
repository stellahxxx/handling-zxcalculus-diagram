import numpy as np
import itertools
import svgparser as sp

def xshift_list(wires_n,edge_len):
    """Create positions for the wire ends on a morphism edge.

    Args:
        wires_n (int): The number of wires.
        edge_len (float): The length of the morphism edge in LaTeX.

    Returns:
        A list of xshift values.
    """    
    shift_list = [0] * wires_n
    if wires_n % 2 == 0:
        interval = edge_len/wires_n
        shift_list[0] = -edge_len/2 + interval/2
    else:
        interval = (edge_len/2) / ((wires_n-1)/2)
        shift_list[0] = -edge_len/2
    for i in range(1,wires_n):
        shift_list[i] = shift_list[i-1] + interval
    return shift_list

def organize_wires(morphismlist,wirelist,edge_len=5.0):
    """Move the wire ends according to the xshift values.
    
    Args:
        morphismlist (list): The list of morphisms after connection stage.
        wirelist (list): The list of wires after connection stage.
        edge_len (float): The length of the morphism edge in LaTeX.
    """    
    for morphism in morphismlist:
        morphism.sortConnection()
        south,north = [],[]
        for connection in morphism.connections:
            angle = connection[1]
            if angle[1] < 0:
                south.append(connection)
            else:
                north.append(connection)
        for side in [south,north]:
            wires_n = len(side)
            if wires_n > 1:
                shift_list = xshift_list(wires_n,edge_len)
                for j,[wire,_,i] in enumerate(side):
                    wire.changeShift(i,shift_list[j])

def get_ref_centre(nodelist):
    """Choose a node as the diagram centre and find the unit distance.
    
    Find the shortest distance between two nodes and use it as the unit distance of the 
    diagram grid. Choose one of these two nodes as the diagram centre.

    Args:
        nodelist (list): A list of nodes

    Returns:
        The absolute position of the centre node and the unit distance of the diagram.
    """    
    centres = [node.centre for node in nodelist]
    min_d = sp.dist(centres[0], centres[1])    
    min_p0,min_p1 = centres[0], centres[1]
    for p0, p1 in itertools.combinations(centres, 2):
        d = sp.dist(p0,p1)
        if d < min_d:
            min_d = d
            min_p0,min_p1 = p0,p1   
    min_x = abs(min_p0[0] - min_p1[0])
    min_y = abs(min_p0[1] - min_p1[1])
    unit_d = max(min_x, min_y)
    return [min_p0,unit_d]

def get_relative_pos(abs_pos,ref_centre,unit_d,unit=1.0): 
    """Calculate the relative position according to a reference position.

    Args: 
        abs_position (list): The absolute position of the point.
        ref_centre (list): THe absolute position of the reference point.
        unit_d (float): The unit distance of the diagram.
        unit (float): The unit length of the diagram grid.

    Returns:
        The relative position of the point in the grid.
    """
    rel_x = round((abs_pos[0] - ref_centre[0])/unit_d)*unit
    rel_y = -round((abs_pos[1] - ref_centre[1])/unit_d)*unit  # Different coordinate system
    return [rel_x,rel_y]

def transform_angle(sub,round_value=10.0):
    """Round the angle.
    
    Transform the direction vector to an angle value between 0 to 360. Round the angle with the 
    interval of round_value.
    
    Args:
        sub (list): The direction vector.
        round_value (float): The interval of rounding. 
        
    Returns:
        The rounded angle. 
    """
    x,y = sub  
    x,y = -x,-y  # let the node be the centre
    x += 0.000001  # avoid divide zero
    y = -y  # origin is at bottom-left corner in latex
    angle = np.arctan(y/x)* 180 / np.pi
    angle = round(angle/round_value)*round_value
    if y > 0 and angle < 0: 
        angle = angle + 180
    if y < 0:
        if angle < 0:
            angle = angle + 360
        else:
            angle = angle + 180
    return angle

def transform_direction(angle,morphism_dir=None):
    """Put the wire ends to the morphisms north and south side.
    
    Args:
        angle (float): The angle value betwwen 0 to 360.
        morphism_dir (str): The side of the mophism.
    
    """
    if morphism_dir == None:
        # If not a morphism, round it to four directions. 
        return round(angle/90.0)*90
    else:
        if morphism_dir == "north":
            return 90
        elif morphism_dir == "south":
            return 270
        else:
            print "wrong node"
            return 0
            
            
def preprocess(dotlist,morphismlist,nodelist,wirelist,ref_centre,unit_d):
    """The integration of node and wire preprocessing.

    Args:
        dotlist (list): A list of dots.
        morphismlist (list): A list of morphisms.
        nodelist (list): The list of two kinds of nodes.
        wirelist (list): A list of wires.
        ref_centre (list): An absolute position.
        unit_d (float): The unit distance in the diagram.
    """    
    organize_wires(morphismlist,wirelist)
    i = 0
    points = []
    for node in nodelist:
        node.giveId(i)
        i += 1
        relative_pos = get_relative_pos(node.centre,ref_centre,unit_d)
        points.append(relative_pos)
        node.setRelativePos(relative_pos)       

def pos_str(pos):
    """Transform the position into a string.
    
    Args:
        pos (list): A position.

    Returns:
        The string of the position.
    """
    x,y = pos
    return "(%.2f,%.2f)" % (x,y)                    
    
def interface_str(interface,angle):
    """Get the string of an interface used a wire string.
    
    Args:
        interface (list, object): An interface, could be a position or a node.

    Returns
        The string of the interface.
    
    """
    if type(interface) == list:  # Interface is a point
        return "+(%.2f,%.2f)" % (interface[0], interface[1])
    else:  # interface is a node object
        if interface.getType() == "dot":  # Interface is a dot
            return "(%d.center)" % (interface.node_id)
        else:  # Interface is a morphism
            if angle >= 0 and angle <= 180:
                return "(%d.north)" % (interface.node_id)
            else:
                return "(%d.south)" % (interface.node_id)


def node_wire_info(connectnode,sub,wire):
    """Calculate the angle of the wire connecting the node.
    
    Args:
        sub (list): A direction vector.
        wire (object): A wire object.
    
    Returns:
        The string of the interface and the angle. 
    """
    angle = transform_angle(sub)
    node_str = interface_str(connectnode,angle)
    if connectnode.getType() == "morphism":
        morphism_dir = node_str[-6:-1]  # The result could be "north" or "south"
        angle = transform_direction(angle,morphism_dir)
    return [node_str,angle]
                    
def draw_node(node):
    """Compose the command of drawing a node in LaTeX.
    
    args:
        node (object): A node object.
        
    Returns:
        The string of command.    
    """
    return "node [%s%s%s] (%d) at %s {%s}; *" % (node.colour, node.getType(), node.getOrientStr(),
                                                     node.node_id, pos_str(node.relative_pos), node.func_name)

def draw_wire(out_str,in_str,out_angle=None,in_angle=None):
    """Compose the command of drawing a wire in LaTeX.
    
    args:
        out_str (str): The string of out interface.
        in_str (str): The string of in interface.
        out_angle (float): The wire's angle of out interface.
        in_angle (float): The wire's angle of in interface.
        
    Returns:
        The string of command.    
    """
    if out_angle == None or in_angle == None:
        return "draw %s to %s; *" % (out_str, in_str)
    else:
        return "draw [out=%d,in=%d] %s to %s; *" %(out_angle, in_angle, out_str, in_str)

def draw_longwire(out_str,in_str,out_angle,in_angle,interpoints_str):
    """Compose the command of drawing a long wire with inter points in LaTeX.
    
    args:
        out_str (str): The string of out interface.
        in_str (str): The string of in interface.
        out_angle (float): The wire's angle of out interface.
        in_angle (float): The wire's angle of in interface.
        interpoisnt_str (str): The command string of inter poitns.
        
    Returns:
        The string of command.          
    """
    return "draw %s%s%s; *" %(out_str, interpoints_str, in_str)
        
    
def create_diagram(dotlist,morphismlist,wirelist):
    """Create the normalised diagram and compose LaTeX commands.
    
    Do preprocessing for the elements first. Start with a begin command. Then draw nodes and wires and end
    with a end command. The rules of calculating the in_angles and out_angles of the inter-wires: 
    current.out_angle = opposite previous.in_angle, current.in_angle is calculated by the absolute positions 
    of the current and next inter points.
    
    Args: 
        dotlist (list): A list of dot objects.
        morphismlist (list): A list of morphismlist.
        wirelist (list): A list of wires.
        
    Returns:
        The commands to generate a diagam in LaTeX.
    """
    nodelist = dotlist+morphismlist
    # Preprocessing
    [ref_centre,unit_d] = get_ref_centre(nodelist)
    preprocess(dotlist,morphismlist,nodelist,wirelist,ref_centre,unit_d)
    
    command =""  # The start of the comamnds
    
    # Generate commands to draw nodes in the LaTeX diagram
    for node in nodelist:      
        node_str = draw_node(node)
        command += node_str
        out_in = [[0,0],[0,0]]  # To record absolute position of out_node and in_node
        
    # Generate commands to draw wires in the LaTeX diagram
    for wire in wirelist:
        connected_ends = []  # Record the ends to check if there is some ends connecting to nothing
        for [connectnode, sub, i, shift] in wire.connections:
            if i == 0:  # connectnode == out_node
                out_in[0] = connectnode.centre
                [out_str, out_angle] = node_wire_info(connectnode,sub,wire)
                if shift != 0:
                    shift_str = "([xshift=%.3fmm]" % (shift)
                    out_str = shift_str + out_str[1:]
            if i == 1:  # connectnode == in_node 
                out_in[1] = connectnode.centre
                [in_str, in_angle] = node_wire_info(connectnode,sub,wire)
                if shift != 0:
                    shift_str = "([xshift=%.3fmm]" % (shift)
                    in_str = shift_str + in_str[1:]
            connected_ends.append(i)
        # At least one end connects to nothing
        # These ends connect to a point
        if len(connected_ends) < 2:  
            rest_i = [i for i in [0,1] if i not in connected_ends]
            for i in rest_i:
                end = wire.ends[i]
                out_in[i] = wire.ends[i]
                # Find the relative position of the end point, make wire connect to this point
                relative_pos = get_relative_pos(end,ref_centre,unit_d)
                if i == 0:                     
                    sub = [x-y for x, y in zip(wire.pointlist[1],end)]
                    out_angle = transform_direction(transform_angle(sub))
                    out_str = interface_str(relative_pos,out_angle)
                if i == 1: 
                    sub = [x-y for x, y in zip(wire.pointlist[-2],end)]
                    in_angle = transform_direction(transform_angle(sub))
                    in_str = interface_str(relative_pos,in_angle)
                    
        # If the length of the wire exceeds the threshold, find inter points and draw a long wire
        wire_len = wire.getLength()
        len_times = wire_len/unit_d
        if wire_len > unit_d * 1.5:
            point_n = int(round(len_times))
            if point_n > 4:
                point_n = 4  #  Don't want too many inter points even if the wire is very long
            interpoints = wire.refinePoints(point_n)[1:-1]  # Get the absolute inter points' positions. 
                                                            # Remove the start point and the end point
            interpoints_str = ""
            # The relative position of the current point references to the previous point position
            # So use loop to create a list of relative positions
            relative_points = []
            for i,point in enumerate(interpoints):
                if i==0:
                    rel_point = get_relative_pos(point,out_in[0],unit_d/2,0.5)
                else:
                    rel_point = get_relative_pos(point,interpoints[i-1],unit_d/2,0.5)
                relative_points.append(rel_point)
            # Create the string of the long wire
            previous_in_angle = 0
            for i,point in enumerate(relative_points): 
                current_point = interpoints[i]
                if i == 0:
                    p_out_angle = out_angle
                    previous_point = out_in[0]
                else:
                    p_out_angle = (previous_in_angle+180)%360  # The opposite direction of the in_angle of the previous point
                    previous_point = interpoints[i-1]                
                sub = [current_point[0]-previous_point[0],current_point[1]-previous_point[1]]
                p_in_angle = transform_angle(sub)
                p_in_angle = transform_direction(p_in_angle)  # The angle only have four directions
                previous_in_angle = p_in_angle
                point_str = " to [out=%d, in=%d] +%s" %(p_out_angle,p_in_angle,pos_str(point))
                interpoints_str += point_str
            last_out = (p_in_angle+180)%360
            last_str = " to [out=%d, in=%d]" % (last_out,in_angle)
            interpoints_str += last_str
            wire_str = draw_longwire(out_str,in_str,out_angle,in_angle,interpoints_str)
        else:
            wire_str = draw_wire(out_str,in_str,out_angle,in_angle)
        command += wire_str
    return command
