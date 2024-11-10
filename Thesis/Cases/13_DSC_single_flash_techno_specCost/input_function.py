# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 14:38:12 2023

@author: lgalieti

@co-author: tmerbecks
"""
# from Simulator.DirectCycles.single_flash import DirectCycle as single_flash
from Thesis.PowerPlants.single_flash import DirectCycle as single_flash
from FluidProperties.fluid import Fluid
from Simulator.streams import MaterialStream

    
#### optimization of a single flash direct steam cycle
def Objective_Function(Variables, Parameters):

    try:

        cycle = calc_Cycle(Variables, Parameters)

        f0 = cycle.specific_cost
        objectives = [f0]
        constraints = []

    except:

        objectives = [1e6]
        constraints = []

    return objectives, constraints


def init_cycle(Variables, Parameters):
    Cycle = single_flash()
    Cycle.drilling_costs = Parameters["DrillingCosts"]
    Cycle.condenser.deltaP_cold = Parameters["Condenser dP"]
    Cycle.coolingpump.eta_isentropic = Parameters["Cooling Pump IsenEff"]

    hot_fluid = Fluid(Parameters["Hot fluid comp"], engine = Parameters["Hot fluid engine"])
    hot_fluid_stream = MaterialStream(hot_fluid, m= Parameters["Hot fluid mass flow"])
    hot_fluid_stream.update(Parameters["Hot fluid input spec"], Parameters["Hot fluid input1"], Parameters["Hot fluid input2"])

    if Parameters["Hot fluid tables"]:
        hot_fluid_tab = Fluid(Parameters["Hot fluid comp"], engine="tables", filename=Parameters["Hot fluid table path"])
        hot_fluid_tab_stream = MaterialStream(hot_fluid_tab, m=Parameters["Hot fluid mass flow"])

        Cycle.set_geofluid(hot_fluid_stream, interpolation=hot_fluid_tab_stream)
    else:
        Cycle.set_geofluid(hot_fluid_stream)

    cold_fluid = Fluid(Parameters["Cold fluid comp"], engine = Parameters["Cold fluid engine"])
    cold_fluid_stream = MaterialStream(cold_fluid, m= 1)
    Cycle.set_coolant(cold_fluid_stream)

    Cycle.condenser.deltaT_pinch = Variables[2]

    variables_ = (Variables[0], Variables[1])

    return Cycle, variables_


def calc_Cycle(Variables, Parameters):

    cycle, variables_ = init_cycle(Variables, Parameters)

    cycle.calc(*variables_)

    return cycle


def PostProcessing(Variables, Parameters):

    cycle, variables_ = init_cycle(Variables, Parameters)

    cycle.calc(*variables_)

    M_profile = []
    W_profile = []
    PC_profile = []
    C_profile = []
    NPV_profile = []
    LCOE_profile = []

    Parameters["TestMassRates"].append(Parameters["Hot fluid mass flow"])
    for m in Parameters["TestMassRates"]:
        cycle.update_mass_rate(m)

        M_profile.append(m*1)
        W_profile.append(cycle.net_power*1)
        PC_profile.append(cycle.primary_equipment_cost*1)
        C_profile.append(cycle.cost*1)
        NPV_profile.append(cycle.NPV*1)
        LCOE_profile.append(cycle.LCOE*1)

    results = {"NetPow_elec": cycle.net_power_elec,
               "CyclePow_elec": cycle.cycle_power_elec,
               "ParasiticPow_elec": cycle.parasitic_power_elec,
               "NetPow": cycle.net_power,
               "CyclePow": cycle.cycle_power,
               "ParasiticPow": cycle.parasitic_power,
               "Qin": cycle.Q_in,
               "Qin_max": cycle.Q_in_max,
               "Qout": cycle.Q_out,
               "eta_I_cycle": cycle.eta_I_cycle,
               "eta_I_recov": cycle.eta_I_recov,
               "eta_I_plant": cycle.eta_I_plant,
               "eta_II_BF": cycle.eta_II_BF,
               "eta_II_FUNC": cycle.eta_II_FUNC,
               "Exergy losses": cycle.exergy_losses,
               "Tmin": cycle.Tmin,
               "Cost": cycle.cost,
               "PrimaryCosts": cycle.primary_equipment_cost,
               "SecondaryCosts": cycle.secondary_equipment_cost,
               "ConstructionCosts": cycle.construction_cost,
               "SpecificCost": cycle.specific_cost,
               "Costs": cycle.costs,
               "NPV": cycle.NPV,
               "NPV_profile": cycle.NPV_profile,
               "ROI": cycle.ROI,
               "IRR": cycle.IRR,
               "LCOE": cycle.LCOE,
               "M_profile": M_profile,
               "W_profile": W_profile,
               "PC_profile": PC_profile,
               "C_profile": C_profile,
               "NPVs_profile": NPV_profile,
               "LCOE_profile": LCOE_profile,
               }

    return results