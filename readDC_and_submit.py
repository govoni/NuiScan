#!/usr/bin/python

import os
import sys
import subprocess
import operator
from ROOT import TFile, TH1F, TCanvas, gStyle, TLine
from commands import getstatusoutput
from operator import itemgetter


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----

def runLimitCalc (filename) :

    filenameBash   = filename+".submit.sh"
    filenameResult = filename+".limit.txt"

    argslist = [
      'combine', 
       '-M' , 
       'Asymptotic', 
      filename,
      ' &> ',
      filenameResult
    ]

    f = open (filenameBash, 'w')
    f.write ("#/bash/sh \n")
    os.getcwd()
    f.write ("cd "+os.getcwd()+"\n")
    f.write ("cd CMSSW_6_2_0_pre3/src/ \n")
    f.write ("eval `scramv1 runtime -sh` \n")
    f.write ("cd - \n")
    f.write ("cd /tmp/ \n")
    f.write (' '.join(argslist))
    f.write("\n")
    os.getcwd()
    #copyremote = "cp "+filenameResult+" "+os.getcwd()
    #f.write (copyremote)
    #f.write("\n")

    f.close ()

    os.system("chmod +x "+filenameBash)

    print "bsub -q 8nm "+filenameBash
    #os.system("bsub -q 8nm "+filenameBash)


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----

def getLimitFromFile (filename) :
    filenameResult = filename+".limit.txt"
    f = open (filenameResult, 'r')
    calcLimit = f.readlines()

    thisLimit = [line for line in calcLimit.split ('\n') if line.find ('Expected 50.0') != -1][0].split ()[4]  
    return thisLimit



# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----


def clean (basename) :
    getstatusoutput('rm ./' + basename + '*')


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----


def lookAtSystematics (datacardname) :

# open the datacard file
# ---- ---- ---- ---- ---- ---- ---- ----

    print 'Opening original input datacard: ', datacardname 
    lines = open (datacardname, 'r').read().split ('\n')
    nametag = datacardname.split ('/')[-1].replace ('.txt', '')
    thepath = datacardname.replace (nametag + '.txt', '')

    print "nametag="+nametag
    print "thepath="+thepath

# separate header and systematics
# ---- ---- ---- ---- ---- ---- ---- ----
    
    gStyle.SetGridStyle (1)
    gStyle.SetGridColor (15)
#    gStyle.SetGridWidth (float (0.5))
    systime = 0
    header = []
    systematics = []
    for linea in lines:
        if '---' in linea : continue
        if systime == 0 :
            header.append (linea)
            if linea.split (' ')[0] == 'rate' :
                systime = 1
        else:
            systematics.append (linea)

    systematics = [elem for elem in systematics if len (elem.split ()) > 0]

# run the actual result with the original datacard
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 

    runLimitCalc (datacardname)

# remove, one at a time, one systematic, and run the limit 
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 

    syslist = []
    syslist.append ('NOMINAL')

    for it in range (len (systematics)) :
        elements = systematics[it].split ()
        syslist.append (systematics[it].split ()[0])
        if len (elements) == 0 : continue

        filename = thepath + 'tempo.remove.' + str (it) + '.' + systematics[it].split ()[0] + '.' + nametag
        f = open(filename, 'w')
        for linea in header: f.write (linea + '\n')
        for it1 in range (len (systematics)) :
            if (it1 == it) : continue
            if len (systematics[it1].split ()) == 0 : continue
            f.write (systematics[it1] + '\n')
        f.close ()

        runLimitCalc (filename)

# run the limit with no systematics
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 

    filename = thepath + 'tempo.stats.' + str (0.) + '.txt'
    f = open(filename, 'w')
    for linea in header: f.write (linea + '\n')
    f.close ()
    runLimitCalc (filename)

# add, one at a time, only one systematic source, and run the limit
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 

    for it in range (len (systematics)) :
        elements = systematics[it].split ()
        if len (elements) == 0 : continue

        filename = thepath + 'tempo.add.' + str (it) + '.' + systematics[it].split ()[0] + "." +  nametag
        f = open(filename, 'w')
        for linea in header: f.write (linea + '\n')
        f.write (systematics[it] + '\n')
        f.close ()

        runLimitCalc (filename)

# clean
# ----

    #clean (thepath + 'tempo') 
    #clean ('roostats') 


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----


if __name__ == '__main__':


    if len (sys.argv) < 2 : 
        print 'input datacard folder missing\n'
        exit (1)

    folderName = sys.argv[1].split ('/')[-1] + '_copy'
    result = getstatusoutput ('rm -rf ' + folderName)
    if result[0] == 0 : print 'NB folder ' + folderName + ' cleaned, being replaced'

    currentFolder = getstatusoutput ('pwd')[1]
    getstatusoutput ('cp -r ' + sys.argv[1] + ' ./' + folderName)

    listOfDatacards = []
    for elem in getstatusoutput ('ls ' + str (folderName) + ' | grep txt')[1].split ('\n'):
        listOfDatacards.append (currentFolder + '/' + folderName + '/' + str (elem))

    for datacard in listOfDatacards :
        lookAtSystematics (datacard)









