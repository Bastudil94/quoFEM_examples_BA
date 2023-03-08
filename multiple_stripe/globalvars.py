#----------------------------------------------------
# Define the initial values for global variables that are shared between modules. 
# It is not needed to have all variables here, 
# more variables can be dynamically created and stored in this module while running other modules.
#  
# call this module as: 
#   import globalvars as gv
# then, call any variable as gv.variablename
#----------------------------------------------------


# model:
Modelo = "model1";

# Earthquake
EqkDataset = "FEMAP695_FarField"

par_Scaling ={
"CuTa":1.25, 
"SDC":"SDC_Dmax",
}

SeismicIndex = 1;
ScaleX = 1.0
GMdirection_1 =1
SubStep = 1.0;

# import at bottom to overwrite
from params import *

