# b.astudillo, 2023
import os, sys
import re
import globalvars as gv


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
