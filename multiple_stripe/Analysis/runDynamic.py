

import openseespy.opensees as ops;
import pandas as pd;
import os, sys
import re

import globalvars as gv

import Analysis.CustomProc as ba


import numpy as np

    


def set_GroundMotionInput():

    #Sismo 1 --------------	
    gv.accelSeries = 2										
    gv.accfactor = gv.g*gv.ScaleX*gv.initialFactor1   ;  # Ground Motion scaling factor

    gv.p = gv.accfactor*gv.accData; # scaled ground accelerations

    ops.timeSeries('Path',gv.accelSeries,'-values',*gv.p,'-dt',gv.dtF,'-factor',1)
    ops.pattern('UniformExcitation',2,gv.GMdirection_1,'-accel',gv.accelSeries)

def set_Recorders():

    # Current info
    ops.printModel('-file',ba.recName('info'))

    # Ground recorders
    ops.recorder('Node','-file',ba.recName('GMAccel_Dir1'),'-time','-dT',gv.dtR,'-time','-timeSeries',gv.accelSeries,'-node',gv.BaseNode,'-dof',1,'accel')

    # fnodes recorders
    ops.recorder('Node','-file',ba.recName('LD'),'-time','-dT',gv.dtR,'-node',*gv.fnodes,'-dof',1,'disp')
    ops.recorder('Node','-file',ba.recName('LAcc'),'-time','-dT',gv.dtR,'-timeSeries',gv.accelSeries,'-node',*gv.fnodesGround,'-dof',1,'accel')



def set_AnalysisParam():
    #### Define Analysis parameters

    # Perform analysis to get equilibrium with lateral loads
    gv.tol = 1.0e-8*1; # max tolerance allowed (unit dependent)

    # Analysis
    ops.system("UmfPack") # create SOE.    Umfpack comes with own numbering.
    ops.numberer("RCM") # create DOF number
    ops.constraints("Plain") # create constraint handler
    ops.integrator('Newmark',  0.5,  0.25) # constant average acceleration: the reason is bc unconditionally stable (error bounded). Linear is cond stable. Implicit: depends on previous steps and the current step. Almost always implies iterations.
    ops.test('EnergyIncr', gv.tol, 50) # create test. 20, 25 iterations should be enough.
    ops.algorithm("KrylovNewton") # create algorithm
    ops.analysis("Transient") # create analysis object
   

def SolverLoop():

    # Returns current time in the analysis
    ok = ops.analyze(1,gv.dtA);
    tcurr = ops.getTime()

    #### Solve Loop
    # enter analysis loop
    print('Running Nonlinear Dynamic Analysis...')

    while ok == 0 and np.abs(tcurr) < np.abs(gv.TimeMax):

        ok = ops.analyze(1,gv.dtA) 

        # add custom methods to solve non-convergence
        # ----

        # current time
        tcurr = ops.getTime()        

    print ('ok: %d' %ok)

def runDynamic():
    
    ba.F_ReadEarthquakeInfo(gv.EqkDataset,gv.SeismicIndex)
    ba.set_FolderNames("RHA");
    
    set_GroundMotionInput()
    set_Recorders()
    set_AnalysisParam()

    SolverLoop();


if __name__ == "__main__":
    runDynamic();

