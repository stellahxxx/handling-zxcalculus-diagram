# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 22:21:32 2016

@author: Administrator
"""

from sklearn import svm, linear_model
import svgparser as sp
import element as elm
import segment as sgm
import dataset as ds


def collectData(filename):
    """Collect freehand drawn path information from the file.

    Args:
        filename (str): The name of a SVG file containing training data. The file should only contain
                        one type of nodes.

    Returns:
        data (list): A list of attributes,

    """
    data = []
    tree = sp.loadFile(filename)
    pathlist = sp.loadPaths(tree)
    shapelist = sgm.segmentPath(pathlist, train=True)[0]  # Skip segmentation when training
    for shape in shapelist:
        shape.getAttributes()
        data.append(shape.attributes)
    return data


def generateData(nodetype, num):
    """ Generate training data by code.

    Use code in the dataset.py to generate node like paths and give them labels. Then transform these paths into shape
    objects and calculate their attributes.

    Args:
        nodetype (str): Type must be 'dot' or 'morphism'.
        num (int): The number of data to generate.

    Returns:
        data (list): A list of attributes.
        y (list): A list of labels.
        data and y have the same length and each pair of elements on the same position are corresponding.
    """
    data = []
    y = []
    if nodetype == 'dot':
        dotpathlist = [ds.generateDotPath() for _ in xrange(num)]
        # Skip segmentation when training. Only has one hypothesis without segmentation.
        shapelist = sgm.segmentPath(dotpathlist, train=True)[0]
        for shape in shapelist:
            shape.getAttributes()
            data.append(shape.attributes)
        newy = [1] * len(data)  # 0 corresponds to dot nodes.
        y.extend(newy)
    elif nodetype == 'morphism':
        morphismpathlist = [ds.generateMorphismPath() for _ in xrange(num)]
        shapelist = sgm.segmentPath(morphismpathlist, train=True)[0]
        for shape in shapelist:
            shape.getAttributes()
            data.append(shape.attributes)
        newy = [-1] * len(data)  # 1 corresponds to morphism nodes.
        y.extend(newy)
    else:
        pass
    return data, y


def trainSVM(filenames, labels, dotnum, morphismnum):
    """Use both existing data and generated data to train the SVM classifier.

    Args:
        filenames (list): A list of filename strings. Each file should only contain one type of nodes.
        labels (list): A list of node label 0 or 1.
        filenames and labels have the same length and each pair of elements on the same position are corresponding.

    Returns:
        A classifier object.
    """
    data = []
    y = []
    if len(filenames) != len(labels):
        print('wrong input')
    else:
        for filename, label in zip(filenames, labels):
            newdata = collectData(filename)
            newy = [label] * len(newdata)
            data.extend(newdata)
            y.extend(newy)
        dotdata, doty = generateData('dot', dotnum)
        mordata, mory = generateData('morphism', morphismnum)
        data.extend(dotdata)
        y.extend(doty)
        data.extend(mordata)
        y.extend(mory)
        clf = svm.LinearSVC()
        clf.fit(data, y)
    return clf


def predict(hypotheses, clf):
    """ Give prediction of all the paths in all hypotheses.

    All the open shapes and concave shapes are considered as wires. All the closed and convex shapes are classified
    into dots and morphisms.

    Args:
        hypotheses (list): A list of hypothesis. Each hypothesis is a shapelist containing shapes.
        clf (obj): The SVM classifier.

    Returns:
        A list of classification results. Each results contains a wirelist, a dotlist and a morphsimlist.
    """
    classifications = []
    for shapelist in hypotheses:
        wirelist = []
        dotlist = []
        morphismlist = []
        for shape in shapelist:
            # If a shape is not a closed shape or is concave, we consider it as a wire.
            if shape.openCheck() or shape.convexCheck():
                wirelist.append(elm.wire([shape.end1, shape.end2], shape.pointlist))
            else:  # All the closed convex shapes are classified by the SVM classifier.
                shape.getAttributes()
                pred = clf.predict([shape.attributes])
                #confidence = clf.predict_proba([shape.attributes])
                if pred == [1]:
                    dotlist.append(elm.dot(shape.centroid, shape.poly, shape.pointlist))
                else:
                    orient = shape.orientation()
                    morphismlist.append(elm.morphism(shape.centroid, shape.poly, shape.pointlist, orient))
        classifications.append([wirelist, dotlist, morphismlist])
        print '==============='
        print('wire:', len(wirelist))
        print('dot:', len(dotlist))
        print('morphism:', len(morphismlist))
    return classifications






