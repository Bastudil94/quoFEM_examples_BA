# b.astudillo, 2023
import pandas as pd;
import os, sys

import globalvars as gv
import CustomFunction as ba


gv.runjob_loc = __file__;



def main():
    
    #--- 
    # folders
    gv.MainFolder = os.path.abspath(os.curdir)

    os.chdir(gv.MainFolder); # go to running folder

    #--- 
    # get PID based on the workdir.i folder name    
    gv.PID = ba.getPID_fromname(gv.MainFolder); 

    #---
    # read extra variables from csv
    tmp = pd.read_csv('variableSet.csv');

    if gv.PID<tmp.shape[0]:
        gv.row,gv.Modelname,gv.SeismicIndex,gv.ScaleX = tmp.loc[gv.PID,:].values.tolist()
        
        print("This is PID: %d"%(gv.PID))
        print("\tVariables read from the .csv file:")
        print("\t",gv.Modelname,gv.SeismicIndex,gv.ScaleX)

        #-------
        # do the analysis here
        #-------

    else:
        # do not do anything because there are no variables for this run
        pass

    # write output
    ba.WriteOutput([gv.PID])
#-----------


if __name__ == "__main__":
    main()


