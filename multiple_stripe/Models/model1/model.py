#--- Call other sources 

import openseespy.opensees as ops;
import pandas as pd;
import os, sys
import globalvars as gv


def genElement(Tag, NI, NJ, Section,Material, trans, elemProc,  **kwargs):

    if elemProc=='elasticBeamColumn':    
        ops.element('elasticBeamColumn',Tag,NI,NJ,gv.sec[Section]["A"],gv.mat[Material]["E"],gv.sec[Section]["Ix"],trans)


def set_units():
    gv.kip    = 1.0;
    gv.inch   = 1.0;
    gv.g      = 386.09; 


def getWsectionAISC(sec):
    # read section from AISC table
    AISC = pd.read_pickle(r"%s/AISC.pkl"%(os.path.dirname(__file__)))
    AISC = AISC[AISC['Type'] == "W"]; # Wsections only

    # save into the dictionary
    for sectionmame in AISC['EDI_Std_Nomenclature']:
        section = AISC.loc[AISC['EDI_Std_Nomenclature'] == sectionmame]
        sec[sectionmame]= {
            'd': float(section.d)*gv.inch,
            'bf': float(section.bf)*gv.inch,
            'tw': float(section.tw)*gv.inch,
            'tf': float(section.tf)*gv.inch,
            'wh': float(section.d - 2*section.tf)*gv.inch,
            'A': float(section.A)*gv.inch**2,
            'Ix': float(section.Ix)*gv.inch**4,
            'Sx': float(section.Sx)*gv.inch**3,
            'Zx': float(section.Zx)*gv.inch**3,
            'rx': float(section.rx)*gv.inch,
            'Iy': float(section.Iy)*gv.inch**4,
            'Sy': float(section.Sy)*gv.inch**3,
            'Zy': float(section.Zy)*gv.inch**3,
            'ry': float(section.ry)*gv.inch,
            'ho': float(section.ho)*gv.inch,
            'J': float(section.J)*gv.inch**4,
            'Cw': float(section.Cw)*gv.inch**6,
        }
    
    return sec

def set_Property_Sections():
    sec = {};
 
    sec["mySection"] = {
        "A": 1*gv.inch**2,
        "Ix": 1*gv.inch**4,
    };

    sec = getWsectionAISC(sec); # append W sections from AISC

    gv.sec = sec;

def set_Property_Materials():
    mat = {};

    mat["A992"] = {
        "Fy": 50*gv.kip/gv.inch**2,
        "E": 29000*gv.kip/gv.inch**2
    }

    gv.mat = mat;


def createmodel():

    ops.wipe()
    
    ops.model('basic','-ndm',2,'-ndf',3) 

    gv.fnodes = [2,3,4,5]; # one node per floor for future reference
    gv.BaseNode = 1;

    gv.fnodesGround = [gv.BaseNode , *gv.fnodes]

    #--- Nodes
    ops.node(       1 ,       0.00000 , 0.0 );
    ops.node(       2 ,       0.00000 , 3281.00000 );
    ops.node(       3 ,       0.00000 , 6781.00000 );
    ops.node(       4 ,       0.00000 , 10281.00000 );
    ops.node(       5 ,       0.00000 , 13781.00000 );

    #--- geomTransf - Automatico 

    ops.geomTransf ('Corotational', 101 );

    #--- mass

    ops.mass(2	,      0.5*15/gv.g , 0.0*0.5*15/gv.g , 0.00000 )
    ops.mass(3	,      0.5*15/gv.g , 0.0*0.5*15/gv.g , 0.00000 )
    ops.mass(4	,      0.5*15/gv.g , 0.0*0.5*15/gv.g , 0.00000 )
    ops.mass(5	,      0.5*15/gv.g , 0.0*0.5*15/gv.g , 0.00000 )

    #--- equalDOF (2D Rigid Diaphgrahms)  


    #--- Fix 

    ops.fix(1,      1 , 1 , 1 )


    #--- Elements

    genElement(   1,       1,        2,    'W30X148','A992',101,'elasticBeamColumn'); 
    genElement(   2,       2,        3,    'W30X148','A992',101,'elasticBeamColumn'); 
    genElement(   3,       3,        4,    'W30X148','A992',101,'elasticBeamColumn'); 
    genElement(   4,       4,        5,    'W30X148','A992',101,'elasticBeamColumn'); 

    print('model done')

def set_ModelDamping():

    nmodes = 2
    wnSq = ops.eigen(nmodes)
    wn = np.array(wnSq)**0.5

    zeta = 0.05


    wi = wn[0]
    wj = wn[1]

    B = np.zeros(shape=(2,2))
    B[0,0] = 1/wi; B[0,1] = wi
    B[1,0] = 1/wj; B[1,1] = wj

    b = np.zeros(2)
    b[0] = 2*zeta
    b[1] = 2*zeta

    a = np.linalg.solve(B,b)

    #             M    KT  KI  Kn
    ops.rayleigh(a[0],0.0,0.0,a[1])

def define_Loads():
    pass;


def main():
    set_units()
    set_Property_Sections()
    set_Property_Materials()
    createmodel()

if __name__ == "__main__":
    main();

