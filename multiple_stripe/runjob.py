import openseespy.opensees as ops;
import pandas as pd;
import os, sys
import re


import globalvars as gv


import Analysis.CustomProc as ba



gv.runningfrom = "designsafe"; # PC designsafe
gv.runjob_loc = __file__;


def main():
    
    #--- 
    # print versions
    printVersions();    

    #--- 
    # folders
    ba.set_FolderNames("initial");  # running folder

    os.chdir(gv.MainFolder); # go to running folder

    gv.PID = ba.getPID_fromname(gv.MainFolder);

    #---
    # read extra variables from csv
    tmp = pd.read_csv('variableSet.csv');

    if gv.PID<tmp.shape[0]:
        gv.Modelname,gv.SeismicIndex,gv.ScaleX = tmp.loc[gv.PID,:].values.tolist()

        ba.set_FolderNames("model_and_result");  # model, and output folder
        #---
        # import modules
        sys.path.insert(0, gv.ModelFolder)
        import model as _model        
        import Analysis.runDynamic as _analysis

        #---
        # run modules
        _model.main()
        _model.set_ModelDamping
        _analysis.runDynamic()

    # write output
    ba.WriteOutput([gv.PID])
#-----------

def printVersions():
    # Check the python and opensees version
    print("\n\n")
    print("Python version: %s" % (sys.version,))
    print("Openseespy version: %s" % ops.version())
    print("\n\n")


if __name__ == "__main__":
    main()


