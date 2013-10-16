#!/usr/bin/python

######################################
# workaround to disable pyroot parser!
import sys
tmpargv = sys.argv
sys.argv = [ '-b','-n' ]
from ROOT import TFile, TH1F, TCanvas, gStyle, TLine
sys.argv = tmpargv
from optparse import OptionParser
######################################

import os
import subprocess
import operator
from commands import getstatusoutput
from operator import itemgetter

import fnmatch


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
    os.system("bsub -q 8nm "+filenameBash)


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

def lookAtSystematics (datacardname,removeNuis,addNuis) :

# open the datacard file
# ---- ---- ---- ---- ---- ---- ---- ----

    print 'Opening original input datacard: ', datacardname 
    lines = open (datacardname, 'r').read().split ('\n')
    nametag = datacardname.split ('/')[-1].replace ('.txt', '')
    thepath = datacardname.replace (nametag + '.txt', '')

    print "nametag = ",nametag
    print "thepath = ",thepath

# separate header and systematics
# ---- ---- ---- ---- ---- ---- ---- ----

    systime = 0
    header = []
    systematics = []
    systematicsName = []
    for linea in lines:
        if '---' in linea : continue
        if systime == 0 :
            header.append (linea)
            if linea.split (' ')[0] == 'rate' :
                systime = 1
        else:
            systematics.append (linea)
            systematicsName.append (linea.split (' ')[0])

    systematics = [elem for elem in systematics if len (elem.split ()) > 0]

    #print "header = ", header

# run the actual result with the original datacard
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 

    runLimitCalc (datacardname)

    syslist = []
    syslist.append ('NOMINAL')


# check if there is some "addNuis"
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 

    if len(addNuis) != 0 :
      filename = thepath + 'tempo.only.subset.' + nametag

      # expand nuisance list to deal with possible wildcards, e.g. *,?
      expandedAddNuis = []
      for subAddNuis in addNuis :
         #print " subAddNuis = ",subAddNuis
         #print " new one: ",fnmatch.filter(systematicsName, subAddNuis) 
         expandedAddNuis += fnmatch.filter(systematicsName, subAddNuis) 
      print "expandedAddNuis = ",expandedAddNuis

      expandedRemoveNuis = []
      for subRemoveNuis in removeNuis :
        expandedRemoveNuis += fnmatch.filter(systematicsName, subRemoveNuis) 
        print "expandedRemoveNuis = ",expandedRemoveNuis

      f = open(filename, 'w')
      for linea in header: f.write (linea + '\n')
      for it in range (len (systematics)) :
        for itAdd in range (len (expandedAddNuis)) :
          if len (systematics[it].split ()) == 0 : continue  # to save last line
          if (systematics[it].split () [0] == expandedAddNuis[itAdd]) :
            # check it is not in the vetoed selection!
            toRemove = False
            for itRem in range (len (expandedRemoveNuis)) :
              if (systematics[it].split () [0] == expandedRemoveNuis[itRem]) :
                toRemove = True
            if not toRemove :
              f.write (systematics[it] + '\n')
      f.close ()

      runLimitCalc (filename)


# check which nuisances need to be removed: removeNuis
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 
    else :
      filename = thepath + 'tempo.remove.subset.' + nametag

      # expand nuisance list to deal with possible wildcards, e.g. *,?
      expandedRemoveNuis = []
      for subRemoveNuis in removeNuis :
         expandedRemoveNuis += fnmatch.filter(systematicsName, subRemoveNuis) 
      print "expandedRemoveNuis = ",expandedRemoveNuis

      f = open(filename, 'w')
      for linea in header: f.write (linea + '\n')
      for it in range (len (systematics)) :
        if len (systematics[it].split ()) == 0 : continue  # to save last line
        toRemove = False
        for itRem in range (len (expandedRemoveNuis)) :
          if (systematics[it].split () [0] == expandedRemoveNuis[itRem]) :
             toRemove = True
        if not toRemove :
          f.write (systematics[it] + '\n')
      f.close ()

      runLimitCalc (filename)



# run the limit with no systematics
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 

    filename = thepath + 'tempo.stats.txt'
    f = open(filename, 'w')
    for linea in header: f.write (linea + '\n')
    f.close ()
    runLimitCalc (filename)


# clean
# ----

    #clean (thepath + 'tempo') 
    #clean ('roostats') 


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----


if __name__ == '__main__':


    #if len (sys.argv) < 2 : 
        #print 'input datacard folder missing\n'
        #exit (1)

    parser = OptionParser()
    parser.add_option("-f", "--folder", dest="folderNameInput",   help="folder name", metavar="DATACARDS")
    parser.add_option("-r", "--remove", dest="removeNuis",   help="list of nuisances to remove",     default='')
    parser.add_option("-a", "--add",    dest="addNuis",      help="subset of nuisances to consider", default='')
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="don't print status messages to stdout")

    (options, args) = parser.parse_args()


    # read nuisances to remove
    removeNuis = options.removeNuis.split(',')
    print "removeNuis=",removeNuis

    # read nuisances to add
    addNuis = options.addNuis.split(',')
    print "addNuis=",addNuis


    # make a copy of the input folder
    folderName = options.folderNameInput.split ('/')[-1] + '_copy_subset'
    result = getstatusoutput ('rm -rf ' + folderName)
    if result[0] == 0 : print 'NB folder ' + folderName + ' cleaned, being replaced'

    currentFolder = getstatusoutput ('pwd')[1]
    getstatusoutput ('cp -r ' + options.folderNameInput + ' ./' + folderName)

    # look for all datacards in that folder
    listOfDatacards = []
    for elem in getstatusoutput ('ls ' + str (folderName) + ' | grep txt')[1].split ('\n'):
        listOfDatacards.append (currentFolder + '/' + folderName + '/' + str (elem))

    # for each datacard perform the nuisances scan
    for datacard in listOfDatacards :
        lookAtSystematics (datacard,removeNuis,addNuis)




