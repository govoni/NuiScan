#!/usr/bin/python

import os
import sys
import subprocess
import operator
from ROOT import TFile, TH1F, TCanvas, gStyle, TLine
from commands import getstatusoutput
from operator import itemgetter


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----

def getLimitFromFile (filename) :
    filenameResult = filename+".limit.txt"
    print "  >> file: "+filenameResult
    f = open (filenameResult, 'r')
    calcLimit = f.read()

    isThereTheLimit = False
    for line in calcLimit.split ('\n') :
      if line.find ('Expected 50.0') != -1 :
        isThereTheLimit = True

    if isThereTheLimit :
     thisLimit = [line for line in calcLimit.split ('\n') if line.find ('Expected 50.0') != -1][0].split ()[4]
    else :
      thisLimit = -1.

    print "thisLimit = "+str(thisLimit)
    return thisLimit


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----


def clean (basename) :
    getstatusoutput('rm ./' + basename + '*')


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----


def lookAtSystematics (datacardname) :

    # open the datacard file
    # ---- ---- ---- ---- ---- ---- ---- ----

    print 'Opening original input datacard: ', datacardname
    nametag = datacardname.split ('/')[-1].replace ('.txt', '')
    thepath = datacardname.replace (nametag + '.txt', '')

    Results = {}
    syslist = []

    # get the actual result with the original datacard
    # ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 

    nominalLimit = getLimitFromFile (datacardname)
    Results['NOMINAL'] = nominalLimit

    # get the result with the modified datacard
    # ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 

    filename = thepath + 'tempo.subset.' + nametag
    thisLimit = getLimitFromFile (filename)
    Results["subset"] = thisLimit

    # get the result with no systematics
    # ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 

    filename = thepath + 'tempo.stats.txt'
    statsLimit = getLimitFromFile (filename)
    Results["STATISTICAL"] = statsLimit

    print "**********************************"
    for kind in Results :
        print " > ",kind," = ",Results[kind]
    print "**********************************"

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----


if __name__ == '__main__':


    if len (sys.argv) < 2 : 
        print 'input datacard folder missing\n'
        exit (1)

    folderName = sys.argv[1].split ('/')[-1] + '_copy_subset'

    currentFolder = getstatusoutput ('pwd')[1]

    listOfDatacards = []
    for elem in getstatusoutput ('ls ' + str (folderName) + ' | grep -v tempo | grep -v limit | grep -v submit | grep txt')[1].split ('\n'):
        listOfDatacards.append (currentFolder + '/' + folderName + '/' + str (elem))

    for datacard in listOfDatacards :
        lookAtSystematics (datacard)


