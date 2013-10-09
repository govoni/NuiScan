#!/usr/bin/python

import os
import sys
import subprocess
import operator
from ROOT import TFile, TH1F, TCanvas, gStyle, TLine
from commands import getstatusoutput
from operator import itemgetter


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----

def getMuError (filename) :
    filenameResult = filename+".mu.txt"
    f = open (filenameResult, 'r')
    calcLimit = f.readlines()

    # e.g.    0    1   2    3                 4
    #        Best fit r: 0.723266  -0.259866/+0.292765  (68% CL)

    thisMuError = [line for line in calcLimit.split ('\n') if line.find ('Best fit r:') != -1][0].split ()[4]
    errorMinus = thisMuError.replace('-','').replace('+','').split("/")[0]
    errorPlus  = thisMuError.replace('-','').replace('+','').split("/")[1]
    error = (errorMinus+errorPlus) / 2.

    return error


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

    # get the actual result with the original datacard
    # ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 
    
    nominalLimit = getMuError (datacardname)
    
    # remove, one at a time, one systematic 
    # ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 

    removingLimits = {}
    removingLimits['NOMINAL'] = nominalLimit
    syslist = []
    syslist.append ('NOMINAL')
    
    for it in range (len (systematics)) :
        elements = systematics[it].split ()
        syslist.append (systematics[it].split ()[0])
        if len (elements) == 0 : continue
        
        filename = thepath + 'tempo.remove.' + str (it) + '.' + nametag
        #f = open(filename, 'w')
        #for linea in header: f.write (linea + '\n')
        #for it1 in range (len (systematics)) :
            #if (it1 == it) : continue
            #if len (systematics[it1].split ()) == 0 : continue
            #f.write (systematics[it1] + '\n')
        #f.close ()

        thisLimit = getMuError (filename)
        removingLimits[systematics[it].split ()[0]] = thisLimit
    
    # get the result with no systematics
    # ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 
    
    filename = thepath + 'tempo.stats.' + str (0.) + '.txt'
    #f = open(filename, 'w')
    #for linea in header: f.write (linea + '\n')
    #f.close ()
    statsLimit = getMuError (filename)

    addingLimits = {}
    addingLimits['NOMINAL'] = statsLimit

    # add, one at a time, only one systematic source
    # ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 

    for it in range (len (systematics)) :
        elements = systematics[it].split ()
        if len (elements) == 0 : continue
        
        filename = thepath + 'tempo.add.' + str (it) + '.' +  nametag
        #f = open(filename, 'w')
        #for linea in header: f.write (linea + '\n')
        #f.write (systematics[it] + '\n')
        #f.close ()
        
        thisLimit = getMuError (filename)
        addingLimits[systematics[it].split ()[0]] = thisLimit

    # filling histograms
    # ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- 
    
    h_removing = TH1F ('removing', 'removing', len (systematics) + 1, 0, len (systematics) + 1)
    h_removing.SetMarkerStyle (20)
    h_removing.SetMarkerColor (9)
    h_removing.SetMarkerSize (2)

    h_adding = TH1F ('adding', 'adding', len (systematics) + 1, 0, len (systematics) + 1)
    h_adding.SetMarkerStyle (4)
    h_adding.SetMarkerColor (9)
    h_adding.SetMarkerSize (2)
    binId = 1

    binId = 1
    for syst in syslist:
        h_removing.GetXaxis ().SetBinLabel (binId, syst)
        h_removing.SetBinContent (binId, float (removingLimits[syst]))        
        h_adding.GetXaxis ().SetBinLabel (binId, syst)
        h_adding.SetBinContent (binId, float (addingLimits[syst]))        
        binId += 1 

    h_sorted_adding = TH1F ('sorted_adding', 'sorted_adding', len (systematics) + 1, 0, len (systematics) + 1)
    h_sorted_adding.SetMarkerStyle (4)
    h_sorted_adding.SetMarkerColor (9)
    h_sorted_adding.SetMarkerSize (2)

    h_sorted_removing = TH1F ('sorted_removing', 'sorted_removing', len (systematics) + 1, 0, len (systematics) + 1)
    h_sorted_removing.SetMarkerStyle (20)
    h_sorted_removing.SetMarkerColor (9)
    h_sorted_removing.SetMarkerSize (2)

    adding_dummy = sorted ([(k, v) for k, v in addingLimits.iteritems ()], key=itemgetter (1))
    sorted_syslist = [k[0] for k in adding_dummy]

    binId = 1
    for syst in sorted_syslist:
        h_sorted_removing.GetXaxis ().SetBinLabel (binId, syst)
        h_sorted_removing.SetBinContent (binId, float (removingLimits[syst]))        
        h_sorted_adding.GetXaxis ().SetBinLabel (binId, syst)
        h_sorted_adding.SetBinContent (binId, float (addingLimits[syst]))        
        binId += 1 

    # final plotting and saving
    # ---- ---- ---- ---- ---- ---- ---- ----

    can = TCanvas ('can', 'can', 30 * len (systematics), 600)
    frac = float (600) / 30. * float (len (systematics))
    can.SetMargin (0.1 * float (frac), 0.025 * float (frac), 0.5, 0.1) #LRBT
    can.SetGridx ()

    l_nominal = TLine (0.,  float (nominalLimit), float (len (systematics) + 1), float (nominalLimit))
    l_nominal.SetLineColor (2)
#    l_nominal.SetLineWidth (float (1))
    l_stats = TLine (0.,  float (statsLimit), float (len (systematics) + 1), float (statsLimit))
    l_stats.SetLineColor (2)
#    l_stats.SetLineWidth (float (1))
    
    bkg = can.DrawFrame (0, h_adding.GetBinContent (1) * 0.9, len (systematics) + 1, h_removing.GetBinContent (1) * 1.1)
    bkg.GetXaxis ().Set (len (systematics) + 1, 0, len (systematics) + 1)
    for i in range (0, len (systematics) + 1) :
        bkg.GetXaxis ().SetBinLabel (i+1, syslist[i])
    bkg.SetTitle (nametag)
    bkg.GetYaxis ().SetTitle ('exp limit')
    bkg.Draw ()
    l_nominal.Draw ('same')
    l_stats.Draw ('same')
    h_adding.Draw ('Psame')
    h_removing.Draw ('Psame')    
    can.Print ('result.' + nametag + '.pdf', 'pdf')
    can.Print ('result.' + nametag + '.gif', 'gif')

    bkg_sorted = bkg.Clone ('bkg_sorted')
    for i in range (0, len (systematics) + 1) :
        bkg_sorted.GetXaxis ().SetBinLabel (i+1, sorted_syslist[i])
    bkg_sorted.Draw ()
    l_nominal.Draw ('same')
    l_stats.Draw ('same')
    h_sorted_adding.Draw ('Psame')
    h_sorted_removing.Draw ('Psame')
    can.Print ('result.sorted.' + nametag + '.pdf', 'pdf')
    can.Print ('result.sorted.' + nametag + '.gif', 'gif')

    outFile = TFile ('outfile.mu.' + nametag + '.root', 'recreate')
    outFile.cd () 
    h_removing.Write ()
    h_adding.Write ()
    h_sorted_removing.Write ()
    h_sorted_adding.Write ()
    outFile.Close ()
    
    #clean (thepath + 'tempo') 
    #clean ('roostats') 


# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----


if __name__ == '__main__':


    if len (sys.argv) < 2 : 
        print 'input datacard folder missing\n'
        exit (1)
        
    folderName = sys.argv[1].split ('/')[-1] + '_copy'
    #result = getstatusoutput ('rm -rf ' + folderName)
    #if result[0] == 0 : print 'NB folder ' + folderName + ' cleaned, being replaced'

    currentFolder = getstatusoutput ('pwd')[1]
    #getstatusoutput ('cp -r ' + sys.argv[1] + ' ./' + folderName)
   
    listOfDatacards = []
    for elem in getstatusoutput ('ls ' + str (folderName) + ' | grep txt')[1].split ('\n'):
        listOfDatacards.append (currentFolder + '/' + folderName + '/' + str (elem))
    
    for datacard in listOfDatacards :
        lookAtSystematics (datacard)   
    


    
    
