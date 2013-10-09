Run the combine on datacards
==============

- to see the impact of each syst in the expected limit, local run: readDC.py
- to see the impact of each syst in the expected limit, runs on a cluster


How to install the environment
--------------

    setenv SCRAM_ARCH slc5_amd64_gcc472
    cmsrel CMSSW_6_2_0_pre3
    cd CMSSW_6_2_0_pre3/src
    cmsenv
    git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
    cd HiggsAnalysis/CombinedLimit
    git pull origin master
    git checkout V03-05-00
    scramv1 b

how to run the script
--------------

get a folder with datacards in:

   svn co svn+ssh://svn.cern.ch/reps/cmshcg/trunk/summer2013/searches/hww2l2v

load the python and CMSSW settings to have the environment

    cd CMSSW_6_2_0_pre3/src
    cmsenv
    cd -

run the readDC.py

   python ./readDC.py /afs/cern.ch/user/g/govoni/work/HWW/limits/datacards/hww2l2v/125
   

how to format this file
--------------


*This will be Italic*

**This will be Bold**

- This will be a list item
- This will be a list item

    Add a indent and this will end up as code
