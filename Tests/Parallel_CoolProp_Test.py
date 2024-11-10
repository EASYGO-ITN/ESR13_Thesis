# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 16:49:47 2023

@author: lgalieti
"""

import CoolProp
from FluidProperties.fluid import Fluid
from Simulator.streams import MaterialStream
Rep = 150000


def CalcProp(P, T, fluid):
    
    
    
    EoS = CoolProp.AbstractState('HEOS', fluid)
    
    EoS.update(CoolProp.PT_INPUTS, P, T)
    # EoS.update(CoolProp.PT_INPUTS, P, T)
    # EoS.update(CoolProp.PT_INPUTS, P, T)
    # EoS.update(CoolProp.PT_INPUTS, P, T)
    # EoS.update(CoolProp.PT_INPUTS, P, T)
    # EoS.update(CoolProp.PT_INPUTS, P, T)
        
    
        
        
        
    
    
    return 0

def CalcTristanProp(P, T, fluid):
    
    TristanFluid = Fluid([fluid,  1], engine="coolprop")
    
   
    TristanFluid.update("PT", P, T)
    # TristanFluid.update("PT", P, T)
    # TristanFluid.update("PT", P, T)
    # TristanFluid.update("PT", P, T)
    # TristanFluid.update("PT", P, T)
    # TristanFluid.update("PT", P, T)
        
   
        
    
    return 0

    
    