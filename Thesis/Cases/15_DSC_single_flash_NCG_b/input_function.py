# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 14:38:12 2023

@author: lgalieti

@co-author: tmerbecks
"""
# from Simulator.BinaryCycles.simple_binary_superheater import ORC as simpleORC
from Thesis.PowerPlants.single_flash_NCG_CarbFix import DirectCycle as single_flash
from FluidProperties.fluid import Fluid
from Simulator.streams import MaterialStream

from scipy.optimize import root_scalar

    
#### optimization of a simple cycle

def Objective_Function(Variables, Parameters):

    try:

        cycle = calc_Cycle(Variables, Parameters)

        f0 = cycle.net_power_elec  # net power is already negative
        objectives = [f0]
        constraints = []

    except:

        objectives = [1e15]
        constraints = []

    return objectives, constraints


def init_cycle(Variables, Parameters):

    Cycle = single_flash()
    Cycle.condenser.deltaP_cold = Parameters["Condenser dP"]
    Cycle.coolingpump.eta_isentropic = Parameters["Cooling Pump IsenEff"]
    Cycle.geofluid_P_out = Parameters["Geofluid_P_out"]

    water = Fluid(["water", 1])
    water.update("TQ", Parameters["Hot fluid input1"], Parameters["Hot fluid input2"])

    hot_fluid = Fluid(Parameters["Hot fluid comp"], engine=Parameters["Hot fluid engine"])

    def q_wat(P):
        hot_fluid.update("PT", P, Parameters["Hot fluid input1"])
        zH2O = hot_fluid.composition[0]
        yH2O = hot_fluid.properties.VapProps.composition[0]
        X = hot_fluid.properties.Q

        Q_wat = X * yH2O / zH2O

        return Q_wat

    def q_search(P):

        error = q_wat(P) - Parameters["Hot fluid input2"]

        return error

    P_min = water.properties.P
    P_max = P_min * (1 + hot_fluid.composition[1])
    iter = 0

    while q_wat(P_max) > Parameters["Hot fluid input2"] and iter < 10:
        P_min = P_max * 1.0
        P_max *= (1 + hot_fluid.composition[1])

        iter += 1

    res = root_scalar(q_search, method="brentq", bracket=[P_min, P_max], rtol=1e-4)
    hot_fluid.update("PT", res.root, Parameters["Hot fluid input1"])

    m = Parameters["Hot fluid mass flow"] * water.properties.H / hot_fluid.properties.H

    hot_fluid_stream = MaterialStream(hot_fluid, m=m)
    hot_fluid_stream.update("PT", res.root, Parameters["Hot fluid input1"])
    if Parameters["Hot fluid tables"]:
        hot_fluid_tab = Fluid(Parameters["Hot fluid comp"], engine="tables", filename=Parameters["Hot fluid table path"])
        hot_fluid_tab_stream = MaterialStream(hot_fluid_tab, m=Parameters["Hot fluid mass flow"])

        Cycle.set_geofluid(hot_fluid_stream, interpolation=hot_fluid_tab_stream)
    else:
        Cycle.set_geofluid(hot_fluid_stream)

    cold_fluid = Fluid(Parameters["Cold fluid comp"], engine=Parameters["Cold fluid engine"])
    cold_fluid_stream = MaterialStream(cold_fluid, m=1)
    Cycle.set_coolant(cold_fluid_stream)

    CO2 = Fluid(["carbondioxide", 1])
    CO2.update("TQ", 300, 0)
    Psat_co2 = CO2.properties.P

    variables_ = [Variables[0] * 1.0,
                  Variables[1] * 1.0,
                  hot_fluid_stream.properties.P + Variables[2]*(Psat_co2 - hot_fluid_stream.properties.P),
                  # hot_fluid_stream.properties.P + Variables[2] * (Parameters["Geofluid_P_out"] - hot_fluid_stream.properties.P)
                  ]

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

        M_profile.append(m * 1)
        W_profile.append(cycle.net_power * 1)
        PC_profile.append(cycle.primary_equipment_cost * 1)
        C_profile.append(cycle.cost * 1)
        NPV_profile.append(cycle.NPV * 1)
        LCOE_profile.append(cycle.LCOE * 1)

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
               "Pin": cycle.geofluid_in.properties.P,
               "Pflash": cycle.P_flash,
               "Xflash": cycle.P_flash / cycle.geofluid_in.properties.P,
               "Tmin": cycle.Tmin,
               "Pmin": cycle.Pmin,
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
               "ncg_handling_power": cycle.ncg_handling_power,
               "ncg_handling_power_elec": cycle.ncg_handling_power_elec,
               "P_Absorption": cycle.Pabsorb,
               "P_in": cycle.geofluid_in.properties.P,
               "P_out": cycle.geofluid_P_out
               }
                # use this excel function to convert a table into rows
                # =FILTERXML( "<t><s>" & SUBSTITUTE( MID(AY2,2,LEN(AY2)-2), ",", "</s><s>" ) & "</s></t>", "//s" )

    return results

if __name__ == "__main__":

    # zc = [0.02, 0.03, 0.05]

    absorb = [0.2, 0.3, 0.4, 0.5, 0.6]

    zc = [0.03 for z in absorb]
    flash = [0.639478522637973 for z in absorb]
    pmin = [12046.687032093228 for z in absorb]

    # pr = [0.639478522637973, 0.4524909234469906, 0.6678690425709841]
    # pmin = [12046.687032093228, 14597.024756737494, 39346.449682905164]
    # absorb = [0.43605155906807164, 0.22947582141747103, 0.764711424710332]

    for i, z in enumerate(zc):

        params = {
            "is Cycle regenerated": False,
            "Hot fluid comp": ["water", 0.95, "carbondioxide", z],
            "Hot fluid engine": "geoprop",
            "Hot fluid table path": "../../../propertyengine_plugins/LookUpTables/SuperDuperTable",
            "Hot fluid tables": True,
            # "Hot fluid comp"           : ["water", 1],
            # "Hot fluid engine"         : "default",
            "Hot fluid input spec": 'TQ',
            "Hot fluid input1": 200+273.15,
            "Hot fluid input2": 0.25,
            "Hot fluid mass flow": 50,
            "Cold fluid comp": ["air", 1],
            "Cold fluid engine": "default",
            "Condenser dP": 120,
            "Cooling Pump IsenEff": 0.6,
            "Working fluid comp": ["nButane", 1],
            "Working fluid engine": "default",
            "MaxSuperheat": 15,
            "MinSuperheat": 2,
            "TestMassRates": [1, 2.5, 5, 10, 25, 50, 100, 150, 200],
            "Geofluid_P_out": 75e5
        }

        variables = [flash[i], pmin[i], absorb[i]]

        plant = calc_Cycle(variables, params)

        print("Wnet:", plant.net_power_elec, "Pabsorb", plant.Pabsorb, plant.ncg_sep_lp.outlet[1].m, plant.ncg_sep_hp.outlet[1].m,)

        # Wnet: -4645646.387616888
        # Pabsorb
        # 3849927.303295906
        # Wnet: -3985065.539792032
        # Pabsorb
        # 2853135.760802215
        # Wnet: -2520457.994928034
        # Pabsorb
        # 5566347.164847434



