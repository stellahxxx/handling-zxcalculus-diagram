# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 19:55:25 2017

@author: Administrator
"""

import itertools
import copy
import svgparser as sp
import element as elm


    
def matchPaths(path1,path2,threshold=10.0):
    """Get the match type of two paths.

    Each path has two ends. Calculate the distance of these ends. If some distance is lower than a threshold,
    then we consider these two path could be grouped together. The match type is how these two paths connected.

    Args:
        path1 (obj): The first path.
        Path2 (obj): The second path.
        threhold (float): The threshold number of distance.

    Returns:
        A list. The first element is the two paths. The second element is 
        the matchtype. 
    """
    matchtype = []
    d0 = sp.dist(path1.end1,path2.end1)
    d1 = sp.dist(path1.end1,path2.end2)
    d2 = sp.dist(path1.end2,path2.end1)
    d3 = sp.dist(path1.end2,path2.end2)
    for i,d in enumerate([d0,d1,d2,d3]):
        if d < threshold:
            matchtype.append(i)
    return [[path1,path2],matchtype]

def iterMatch(pathlist):
    """Iterate the pathlist to find the matches between each pairwise paths. 
    
    All possible match type inlcudes [0],[1],[2],[3],[0,3],[1,2]. Only valid matches
    will be appended into the matchlist.

    Args:
        pathlist (list): The list of all the paths.

    Returns:
        A list of all the matches. Each match includes two paths and thier match type. For example:
        [[element.path instance,element.path instance],[0]]
    """
    matchlist = []
    valid_matchtype = [[0],[1],[2],[3],[0,3],[1,2]]
    for i,path in enumerate(pathlist):
      restpaths = pathlist[(i+1):]
      for restpath in restpaths:
        match = matchPaths(path,restpath)
        if (match[1] in valid_matchtype): 
          matchlist.append(match)
    return matchlist

def refineMatch(matchlist):
    """Refine the matchlist.

    Find matches with three or more paths look like: [path1,path2],[path2,path3].[path1,path3] and add these matches
    into the matchlist.

    Args:
        matchlist (list): The match list only containing matches with two pairing paths.

    Returns:
        matchlist (list): A new match list containing matches with two and three paths.
    """
    newmatchlist = matchlist[:]
    for match in matchlist:
        tempmatchlist = matchlist[:]    
        [path1,path2] = match[0]
        tempmatchlist.remove(match)  # Create a copy list without current match
        match1 = None
        match2 = None
        # Try to find three matches satisfying:
        # match = [[path1,path2],[x]]; match1 = [[path2,path3],[y]]; match2 = [[path1,path3],[z]]
        for othermatch in tempmatchlist:
            if path1 in othermatch[0]:
                match1 = othermatch
            if path2 in othermatch[0]:
                match2 = othermatch
        if match1 != None and match2 != None:
            # Concatenate the paths in match1 and match2
            tempmatch = match1[0][:]
            tempmatch.extend(match2[0])
            tempmatch.sort()
            # Delete duplicate paths and check whether the tempmatch contains exactly 3 paths.
            tempmatch = list(tempmatch for tempmatch,_ in itertools.groupby(tempmatch))
            tempmatch = [tempmatch,[]]
            if (len(tempmatch[0])==3) and (tempmatch not in newmatchlist):
                newmatchlist.append(tempmatch)
    return newmatchlist

def connect2Paths(match):
    """Concatenate two matched paths to one path.

    Must make sure that the points in the new path are sequential. So different match types have different
    concatenating rules. Use deepcopy to protect the original paths.

    Args:
        match (list): Contains two matched paths and their match type.

    Returns:
        A new concatenated path.
    """
    [path1,path2] = match[0]
    if match[1]==[0]:
        revpath1 = copy.deepcopy(path1.pointlist[::-1])
        temppointlist = copy.deepcopy(revpath1)
        temppointlist.extend(path2.pointlist)
        temppointlist = sp.transtoInkscapePath(temppointlist)
        return elm.path(temppointlist)
    elif match[1]==[1]:
        temppointlist = copy.deepcopy(path2.pointlist)
        temppointlist.extend(path1.pointlist)
        temppointlist = sp.transtoInkscapePath(temppointlist)
        return elm.path(temppointlist)
    elif match[1]==[2]:
        temppointlist = copy.deepcopy(path1.pointlist)
        temppointlist.extend(path2.pointlist)
        temppointlist = sp.transtoInkscapePath(temppointlist)
        return elm.path(temppointlist)
    elif match[1]==[3]:
        revpath2 = copy.deepcopy(path2.pointlist[::-1])
        temppointlist = copy.deepcopy(path1.pointlist)
        temppointlist.extend(revpath2)
        temppointlist = sp.transtoInkscapePath(temppointlist)
        return elm.path(temppointlist)
    elif match[1]==[0,3]:
        revpath2 = copy.deepcopy(path2.pointlist[::-1])
        temppointlist = copy.deepcopy(path1.pointlist)
        temppointlist.extend(revpath2)
        temppointlist = sp.transtoInkscapePath(temppointlist)
        return elm.path(temppointlist)
    else: # match[1]==[1,2]
        temppointlist = copy.deepcopy(path1.pointlist)
        temppointlist.extend(path2.pointlist)
        temppointlist = sp.transtoInkscapePath(temppointlist)
        return elm.path(temppointlist)

def connect3Paths(match):
    """Concatenate three matched paths to one path.

    First concatenate two paths and yield a new path. Then concatenate the new path and the rest one.

    Args:
        match (list): Contains three matched paths and a blank match type.

    Returns:
        A new concatenated path.
    """
    [path1,path2,path3] = match[0]
    match1 = matchPaths(path1,path2)  # Need to re-check the match type.
    path12 = connect2Paths(match1)
    match2 = matchPaths(path12,path3)
    path123 = connect2Paths(match2)
    return path123

def connectPath(match):
    """An intergration of the two connect functions.

    Args:
        match (list): Contains two or three matched paths and a match type.

    Returns:
        A new concatenated path.
    """
    if len(match[0])==2:
        return connect2Paths(match)
    elif len(match[0])==3:
        return connect3Paths(match)
        
def yieldBinary(n):
    """Yield 2**n binary numbers.

    The n means there are n matches. The 0 and 1 represent whether we use the match or not in one hypothesis.
    For example, if there are two matches, we will yield '00','01','10','11'. We use the first match but don't
    use the second one in the hypothesis '10'.

    Args:
        n (int): The number of matches.

    Returns:
        Yield strings containing binary numbers.
    """
    maxnum = 2**n
    length = len(bin(maxnum-1))-2  # Length of the string. 2 is the length of '0b'
    for i in range(2**n):
        binary = bin(i)[2:]  # 2 is the length of '0b'
        if len(binary)<length:
            omittedzeros = '0'*(length-len(binary))  # Add omitted zeros.
            binary = omittedzeros+binary
        yield binary
    
def yieldHypotheses(pathlist,matchlist):
    """Yield hypotheses.

    For a matchlist with length=n, yield 2**n hypotheses. Some of the hypotheses might be declined because
    there is a path appear in multiple enabled matches. For example, there are two matches [path1,path2] and
    [path1,path3] found in the pathlist. We yield four hypotheses labeled by binaries '00','01','10','11'.
    The hypothesis '11' will be declined because after we concatenate the first match [path1,path2], path1 is
    already removed from the temporary pathlist. We can not concatenate the [path1,path3].

    Args:
        pathlist (list): A list of paths.
        Matchlist (list): A list of matches. Each match contains two or three matched paths and a match type.

    Returns:
        Yield a valid hypothesis which is a pathlist.

    Raise:
        Exception: The path in the match does not exists in the pathlist.
    """
    n = len(matchlist)
    for binary in yieldBinary(n):  # Each binary corresponds to one hypothesis
        temppathlist = pathlist[:]
        try:
            for i in range(len(binary)):
                if binary[i]=='1':  # Use this match
                    match = matchlist[i]
                    newpath = connectPath(match)  # Concatenate the paths in this match
                    # Check whether the paths in the match are still in the pathlist
                    if all(path in temppathlist for path in match[0]):
                        # Remove the paths in the matches
                        temppathlist = [path for path in temppathlist if path not in match[0]]
                        temppathlist.append(newpath)  # Add the new concatenated path to the pathlist
                    else:
                        raise Exception('path not in pathlist')
            yield temppathlist
        except:
            pass

       
 
def segmentPath(pathlist,train):
    """The integrated function of the segmentation.

    Args:
        pathlist (list): A list of paths.
        train (bool): True if it is in the training process. False otherwise.

    Returns:
        A set of hypotheses. Each hypothesis is a list of shapes.
    """
    hypotheses = []
    if train == False:
        matchlist = iterMatch(pathlist)
        matchlist = refineMatch(matchlist)
        for hypothesis in yieldHypotheses(pathlist,matchlist):
            shapelist = [elm.shape(path.pointlist) for path in hypothesis]
            hypotheses.append(shapelist)
    else:  # If training, skip segmentation.
        shapelist = [elm.shape(path.pointlist) for path in pathlist]
        hypotheses.append(shapelist)
    return hypotheses


def correctPathlist(pathlist):
    """Refine the pathlist if the last path is a correction path.

    Args:
        pathlist (list): A list of paths.

    Returns:
        A set of correction hypotheses and the max intersecton number if the last path is a correction path.
        If not, returns a None for the hypotheses and a 0 for intersection number.
    """
    newpathlist = pathlist[:]  # Copy the pathlist to protect the original one.
    lastpath = pathlist[-1]
    testlist = pathlist[:]  # testlist is a pathlist without the last path.
    testlist.remove(lastpath)
    # Check the intersection between the last path and each path in the testlist. Get a path to be replaced if
    # the last path is a correction.
    [replacedpath,intersect] = lastpath.checkIntersect(testlist)
    if replacedpath!=None:
        newpathlist.remove(replacedpath)
        return [segmentPath(newpathlist,train=False),intersect]
    else:
        return [None,0]