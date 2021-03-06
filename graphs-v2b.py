#!/usr/bin/python

import csv, math, sys, re, numpy, scipy, matplotlib
from pylab import *
from matplotlib import colors

rc('text', usetex=True)
rcParams['text.latex.preamble'].append(r'\usepackage{tipa}')
#rcParams['figure.figsize'] = 8, 3.8

# There is surely a way to make this neater? /Surely/ four try-except
# blocks is excessive and I can parcel them up a bit more nicely?

# hello future self - line_in[0] is the island name.
def dataHelper(dictname,first_line,line_in,posx,posxerr,posy,posyerr):
    dictname[line_in[0]]["type"] = line_in[3]
    try:
        dictname[line_in[0]]["x"].append(float(line_in[posx]))
    except ValueError:
        dictname[line_in[0]]["x"].append("")
    try:
        if posxerr is not None:
             dictname[line_in[0]]["xerr"].append(float(line_in[posxerr]))
    except ValueError:
        dictname[line_in[0]]["xerr"].append("")
    try:
        dictname[line_in[0]]["y"].append(float(line_in[posy]))
    except ValueError:
        dictname[line_in[0]]["y"].append("")
    try:
        if posyerr is not None:
            dictname[line_in[0]]["yerr"].append(float(line_in[posyerr]))
    except ValueError:
        dictname[line_in[0]]["yerr"].append("") 

    return dictname

###
# read the input csv; turn it into something useful
###
def loadData(f,x,xerr,y,yerr):
    first_line = f.readline().split(',')

    # datadict = {"St. Helena": { "type": '',  "x": [x1,...], "xerr": [xerr1,...] "y": [y1,...], 
    #                             "yerr" [yerr1,...]}, 
    #             "Gough": ...}
    islands = {}

    # determine positions of the stuff I care about
    posx    = first_line.index(x)
    if xerr is not None:
        posxerr = first_line.index(xerr)
    else:
        posxerr = None
    posy    = first_line.index(y)
    if yerr is not None:
        posyerr = first_line.index(yerr)
    else:
        posyerr = None

    # stick the data in the places
    for line in f:
        line_in = line.split(',')
        if line_in[0] not in islands and line_in[2] != '':
            islands[line_in[0]] = {"type": '', "x": [], "xerr": [], "y": [], "yerr": []}
            dataHelper(islands,first_line,line_in,posx,posxerr,posy,posyerr)
        elif line_in[0] in islands:
            dataHelper(islands,first_line,line_in,posx,posxerr,posy,posyerr)
        else:
            continue

    return islands

###
# make sure lists are same dimension & properly matched
###
def tidyData(dictionary):
    for key in dictionary:
        zipped = zip(dictionary[key]['x'], dictionary[key]['y'])
        zipped = [(x,y) for (x,y) in zipped if x!= '' and y!= '']
        mustelidae = [list(badger) for badger in zip(*zipped)]
        try:
            dictionary[key]['x'] = mustelidae[0]
            dictionary[key]['y'] = mustelidae[1]
        except IndexError:
            print key + " had no values to unpack"
    return dictionary

###
# put together a semi-replicable list of symbol types
# NB there are data structures for actual replicability
###
def generateSymbols(symbolType, dictionary):
    symbols = {}
    i = 0

    markers = ['x','+','o','*','s','d','^','>','<','v','1','2','3','4','8']
    colours = ['k','r','teal','silver','goldenrod','lightsteelblue','darkorchid','salmon','lightskyblue','chartreuse','saddlebrown','darkslateblue','orchid','indigo','turquoise']
    if symbolType == "islands":
        for key in dictionary:
            if key not in symbols:
                symbols[key] = {'marker': '', 'mfc': '', 'mec': ''}
            symbols[key]['marker'] = markers[i]
            symbols[key]['mfc'] = colours[i]
            symbols[key]['mec'] = colours[i]
            i += 1
    elif symbolType == "components":
        for key in dictionary:
            if key not in symbols:
                symbols[key] = {'marker': '', 'mfc': '', 'mec': ''}
            if dictionary[key]['type'] == "HIMU":
                symbols[key]['mec'] = 'g'
                symbols[key]['mfc'] = 'g'
            if dictionary[key]['type'] == "EMI" or dictionary[key]['type'] == "EMII":
                symbols[key]['mec'] = 'b'
                symbols[key]['mfc'] = 'b'
            symbols[key]['marker'] = markers[i]
            i += 1
    print symbols        
    return symbols

###
# do the thing!
###
if __name__ == '__main__':

    if len(sys.argv) < 3:
	    print >> sys.stderr, "Usage: %s file_in x y (xerr) (yerr)" % sys.argv[0]
	    sys.exit(1)

    # get filename and key args
    file_in = sys.argv[1]
    x = sys.argv[2]
    y = sys.argv[3]
    try:
        xerr = sys.argv[4]
    except IndexError: 
        xerr = None
    try:
        yerr = sys.argv[5]
    except IndexError:
        yerr = None

    # prompt user for relevant input
    figname    = raw_input("Path to save file? ")
    xAxisLabel = raw_input("X axis? Use TeX formatting. ")
    yAxisLabel = raw_input("Y axis? ")

    qLegend    = raw_input("Display legend? y/n ")
    symbolType = raw_input("Plot as islands or components? ")

    ###
    # crunch all the data
    ###
    with open(file_in, 'r') as f:
        islands = loadData(f,x,xerr,y,yerr)

    islands = tidyData(islands)
    print islands

    symbols = generateSymbols(symbolType,islands)
    
    ###
    # TODO this should probably be broken out into its own function
    # plot a graaaaaaph (TODO deal with the not-error-handling!)
    ###
    i = 0
    fig = plt.figure()
    ax = plt.subplot(111)
    for key in islands:
       print key
       #TODO think about what to /actually/ do wrt choosing symbols! does what I've stuck in work?
       if islands[key]['x'] != []:
           for i in range(len(islands[key]['x'])):
               ax.plot(islands[key]['x'][i], islands[key]['y'][i], symbols[key]['marker'], markersize=10,
                       markeredgewidth=1., markerfacecolor = symbols[key]['mfc'], markeredgecolor = symbols[key]['mec'], label=key)
                      #errorbar(islands[key]['x'], islands[key]['y'], islands[key]['yerr'],
	   #         fmt=None,ecolor=symbols[key]['mec'])

#    fill([0,40,40,0],[8000,8000,2000,2000], 'b', alpha=0.1) 

    xlabel(xAxisLabel)
    ylabel(yAxisLabel)

    if qLegend == "y":
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.85, box.height])
        ax.legend(loc='center right', bbox_to_anchor=(1.31, 0.5), numpoints=1, markerscale=1.2,frameon=False, prop={'size':10})

savefig(figname)
