# b.astudillo, 2023
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
Modelname = "a_model_name";

# Earthquake
EqkDataset = "FEMAP695_FarField"

SeismicIndex = "an_eqk_name";
ScaleX = 1.0
GMdirection_1 =1
SubStep = 1.0;

# import at bottom to overwrite what is above
from params import *

