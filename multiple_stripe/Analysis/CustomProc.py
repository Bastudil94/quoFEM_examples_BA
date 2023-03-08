
import pandas as pd;
import os, sys
import re
import globalvars as gv
import numpy as np

def WriteOutput(out):
    for i in range(len(out)):
        out[i] = str(out[i]);
    with open('results.out', 'w') as f:
        f.write(' '.join(out))
    f.close() 

def getPID_fromname(runningFolder):
    # find the process ID, PID:
    match = re.search(r"workdir\.(\d+)", runningFolder)

    if match:
        PID = int(match.group(1)) - 1 ; # -1 to start from 0. e.g., workdir.1 is PID 0
    else:
        PID = 0;

    return PID

def locateRunningFolder(runningfrom):
    # define main folder
    fldr_1 = os.path.abspath(os.curdir);print("current:",fldr_1)    # use in designsafe
    fldr_2 = os.path.dirname(gv.runjob_loc);print("file:",fldr_2)        # use in pc
    #os.getcwd()

    runningFolder = "";

    if runningfrom.lower() == "pc":
         runningFolder = fldr_2;
    elif runningfrom.lower() == "designsafe":
        runningFolder = fldr_1;
    else:
        raise TypeError('Specify an running device name (e.g.,: PC, designsafe). Current: %s'%runningfrom)

    if runningFolder=="":
        raise TypeError('Something is wrong with the path. Running folder is empty, runningFolder: %s'%runningFolder)

    return runningFolder

def set_FolderNames(stage="initial"):

    if stage == "initial":
        # MainFolder. Contains the scripts.
        gv.MainFolder = locateRunningFolder(gv.runningfrom);
        print('\n\n\nFolder info:')
        print('\tMainFolder: %s'%gv.MainFolder)

    elif stage == "model_and_result":

        # Model folder; which contains the model geometry
        gv.ModelFolder = gv.MainFolder + "/Models/" + gv.Modelname 
        
        # ResultFolder. Contains the results (Res_Model).
        gv.ResultFolder = gv.MainFolder + "/Results/"  + "Res_" + gv.Modelname
        os.makedirs(gv.ResultFolder, exist_ok=True)

        # Geometry Folder
        os.makedirs(gv.ResultFolder+'/Result_Geometry', exist_ok=True)

        # Print Folders
        print('\tModelFolder: %s'%gv.ModelFolder)
        print('\tResultFolder: %s'%gv.ResultFolder)        

        return
    
    elif "RHA":
        # Results Dynamic folder
        gv.spacechr = "~"
        gv.ScaleID = "%.2f" %gv.ScaleX
        gv.Codigo = "%s%s%s%s%s" %(gv.GM_Nickname,gv.spacechr,gv.ScaleID,gv.spacechr,gv.Modelname)
        gv.resDir = gv.ResultFolder + '/SF_%s' %gv.ScaleID + '/' + gv.Codigo
        os.makedirs(gv.resDir, exist_ok=True)      
        
        # Print Folders
        print('\tresDir: %s'%gv.resDir)
        print('\n')    



def recName(recname,analysistype = "Dynamic"):
    
    name = '%s/%s.out' %(gv.resDir,recname)
    return name


# read record 
def ReadRecord (inFilename):
    # read record 
    # Written by: BS, DR.

    acc = [];
    dt = 0.0
    npts = 0
    
    # Open the input file and catch the error if it can't be read
    inFileID = open(inFilename, 'r')
    
    # Open output file for writing
    #outFileID = open(outFilename, 'w')

    # Flag indicating dt is found and that ground motion
    # values should be read -- ASSUMES dt is on last line
    # of header!!!
    flag = 0

    # Look at each line in the file
    for line in inFileID:
        if line == '\n':
            # Blank line --> do nothing
            continue
        elif flag == 1:
            # Echo ground motion values to output file
            split = line.split()
            for j in range(len(split)):
                #outFileID.write(split[j]+'\n')
                acc.append(float(split[j])) 
            
        else:
            # Search header lines for dt
            words = line.split()
            lengthLine = len(words)

            if lengthLine >= 4:

                if words[0] == 'NPTS=':
                    # old SMD format
                    for word in words:
                        if word != '':
                            # Read in the time step
                            if flag == 1:
                                dt = float(word)
                                break

                            if flag == 2:
                                npts = int(word.strip(','))
                                flag = 0

                            # Find the desired token and set the flag
                            if word == 'DT=' or word == 'dt':
                                flag = 1

                            if word == 'NPTS=':
                                flag = 2
                        
                    
                elif words[-1] == 'DT':
                    # new NGA format
                    count = 0
                    for word in words:
                        if word != '':
                            if count == 0:
                                npts = int(word)
                            elif count == 1:
                                dt = float(word)
                            elif word == 'DT':
                                flag = 1
                                break

                            count += 1


    inFileID.close()
    #outFileID.close()
    
    if dt==0 or npts==0 or len(acc)==0:
        raise ValueError("ERROR READING THE GROUND MOTION")
    
    
    return dt, npts, np.array(acc)

    
def F_ReadEarthquakeInfo(EqkDataset,SeismicIndex):

    if EqkDataset == 'FEMAP695_FarField':

        ReadGM_Method = "FromFile"
        SeismicPath=r"GM/FarField"

        # Group scale factor (from FEMA P695)
        tmp2 = pd.read_csv(SeismicPath + "/GroupScale.csv")
        print(gv.par_Scaling); # e.g.,: par_Scaling ={"CuTa":1.25, "SDC":"SDC_Dmax",}
        GroupScaleFactor = np.interp(gv.par_Scaling["CuTa"], tmp2["CuTa"], tmp2[gv.par_Scaling["SDC"]], left=None, right=None)

        # Information of all records of the database
        tmp = pd.read_csv(SeismicPath + "/RecordInfo.csv")
        list_NormFactor = [float(tmp["normalizationFactor"][i]) for i in range(len(tmp))]

        list_nickname =     [tmp["ID"][i] for i in range(len(tmp))]
        list_eqkfile =      [tmp["name"][i] for i in range(len(tmp))]
        list_AmplitudSF =   [GroupScaleFactor*list_NormFactor[i] for i in range(len(tmp))]

    
    # find the index (inside the dataset) of the selected record
    if isinstance(SeismicIndex, str):
        if SeismicIndex.isnumeric() == True:
            SeismicIndex = int(SeismicIndex)                    # find by numeric position
        else:
            SeismicIndex = list_nickname.index(SeismicIndex)    # find by name
    
    # find the index inside the dataset of the selected record
    GM_Nickname         = list_nickname[SeismicIndex]
    GM_filename_short   = list_eqkfile[SeismicIndex] ;
    initialFactor1      = list_AmplitudSF[SeismicIndex] ; # This is the scaling factor (amplitud scaling)

    GM_filename_full    = SeismicPath + "/" + GM_filename_short     


    # Read the record
    if ReadGM_Method == "Default":
        dtF=list_dt[SeismicIndex]
        npts = list_npts[SeismicIndex];
        accData = np.loadtxt(GM_filename_full); print('file loaded')
    elif ReadGM_Method == "FromFile":
        dtF, npts, accData = ReadRecord(GM_filename_full);

    # store
    gv.GM_Nickname	                = GM_Nickname
    gv.GM_filename_short			= GM_filename_short
    gv.GM_filename_full		        = GM_filename_full

    gv.dtF				            = dtF
    gv.npts				            = npts
    gv.initialFactor1	            = initialFactor1
    gv.accData			            = accData
    
    gv.TimeMax = gv.dtF*gv.npts

    # dt of Analysis
    gv.dtA = gv.dtF/gv.SubStep

    # dt of Recorders
    gv.dtR = gv.dtA*1.0
        
    print('Earthquake info:')
    print(GM_Nickname,GM_filename_short,dtF,npts,initialFactor1);