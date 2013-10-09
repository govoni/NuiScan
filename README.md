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


how to format this file
--------------


*This will be Italic*

**This will be Bold**

- This will be a list item
- This will be a list item

    Add a indent and this will end up as code
