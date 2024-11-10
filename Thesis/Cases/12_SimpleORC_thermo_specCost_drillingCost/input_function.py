# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 14:38:12 2023

@author: lgalieti

@co-author: tmerbecks
"""
# from Simulator.BinaryCycles.simple_binary_superheater import ORC as simpleORC
from Thesis.PowerPlants.simple_binary_superheater import ORC as simpleORC
from FluidProperties.fluid import Fluid
from Simulator.streams import MaterialStream

    
#### optimization of a simple cycle

def Objective_Function(Variables, Parameters):

    try:

        cycle = calc_Cycle(Variables, Parameters)

        f0 = cycle.net_power_elec
        # f0 = cycle.specific_cost
        objectives = [f0]
        constraints = []

    except:

        objectives = [1e15]
        constraints = []

    return objectives, constraints


def init_cycle(Variables, Parameters):

    Cycle = simpleORC(Parameters["is Cycle regenerated"])
    Cycle.drilling_costs = Parameters["DrillingCosts"]
    Cycle.deltaT_superheat = Parameters["MinSuperheat"]
    Cycle.condenser.deltaP_cold = Parameters["Condenser dP"]
    Cycle.coolingpump.eta_isentropic = Parameters["Cooling Pump IsenEff"]

    hot_fluid = Fluid(Parameters["Hot fluid comp"], engine=Parameters["Hot fluid engine"])
    hot_fluid_stream = MaterialStream(hot_fluid, m=Parameters["Hot fluid mass flow"])
    hot_fluid_stream.update(Parameters["Hot fluid input spec"], Parameters["Hot fluid input1"], Parameters["Hot fluid input2"])

    if Parameters["Hot fluid tables"]:
        hot_fluid_tab = Fluid(Parameters["Hot fluid comp"], engine="tables", filename=Parameters["Hot fluid table path"])
        hot_fluid_tab_stream = MaterialStream(hot_fluid_tab, m=Parameters["Hot fluid mass flow"])

        Cycle.set_geofluid(hot_fluid_stream, interpolation=hot_fluid_tab_stream)
    else:
        Cycle.set_geofluid(hot_fluid_stream)

    cold_fluid = Fluid(Parameters["Cold fluid comp"], engine=Parameters["Cold fluid engine"])
    cold_fluid_stream = MaterialStream(cold_fluid, m=1)
    Cycle.set_coolant(cold_fluid_stream)

    workingfluid = Fluid(Parameters["Working fluid comp"], engine=Parameters["Working fluid engine"])
    workingfluid_stream = MaterialStream(workingfluid, m=1)
    Cycle.set_workingfluid(workingfluid_stream)

    P_crit = workingfluid.state.state.state.p_critical()
    Variables[0] *= P_crit

    workingfluid.update("PQ", Variables[0], 0.5)
    Tsat = workingfluid.properties.T
    Variables[1] += Tsat

    if Variables[1] > Tsat + Parameters["MaxSuperheat"]:
        msg = "Tmax exceeds maximum superheating temperature"
        raise ValueError(msg)

    # Cycle.preheater.deltaT_pinch = Variables[3]
    # Cycle.evaporator.deltaT_pinch = Variables[4]
    # Cycle.superheater.deltaT_pinch = Variables[5]
    # Cycle.condenser.deltaT_pinch = Variables[6]

    variables_ = (Variables[0], Variables[1], Variables[2])

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


    TQ_plot = cycle.plot_TQ(False)

    results = {"NetPow_elec": cycle.net_power_elec,
               "CyclePow_elec": cycle.net_power_elec,
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
               "Pmax": cycle.Pmax,
               "Tmax": cycle.Tmax,
               "Tmin": cycle.Tmin,
               "Cost": cycle.cost,
               "SpecificCost": cycle.specific_cost,
               "SpecificCost_exDrilling": cycle.specific_cost_ex_drilling,
               "Costs": cycle.costs,
               "PrimaryCosts": cycle.primary_equipment_cost,
               "SecondaryCosts": cycle.secondary_equipment_cost,
               "ConstructionCosts": cycle.construction_cost,
               "NPV": cycle.NPV,
               "NPV_profile": cycle.NPV_profile,
               "ROI": cycle.ROI,
               "IRR": cycle.IRR,
               "LCOE": cycle.LCOE,
               "T_coolant": TQ_plot["coolant"]["Temperature"],
               "Q_coolant": TQ_plot["coolant"]["Duty"],
               "T_wf_heating": TQ_plot["wf_heating"]["Temperature"],
               "Q_wf_heating": TQ_plot["wf_heating"]["Duty"],
               "T_wf_cooling": TQ_plot["wf_cooling"]["Temperature"],
               "Q_wf_cooling": TQ_plot["wf_cooling"]["Duty"],
               "T_geofluid": TQ_plot["geofluid"]["Temperature"],
               "Q_geofluid": TQ_plot["geofluid"]["Duty"],
               "T_recu_low": TQ_plot["recu_low"]["Temperature"],
               "Q_recu_low": TQ_plot["recu_low"]["Duty"],
               "T_recu_high": TQ_plot["recu_high"]["Temperature"],
               "Q_recu_high": TQ_plot["recu_high"]["Duty"],
               "M_profile": M_profile,
               "W_profile": W_profile,
               "PC_profile": PC_profile,
               "C_profile": C_profile,
               "NPVs_profile": NPV_profile,
               "LCOE_profile": LCOE_profile,
               "Turbine_Stages": cycle.turbine.n_stages,
               "Turbine_HStages": cycle.turbine.H_stages,
               "Turbine_VStages": cycle.turbine.V_stages,
               "Turbine_SP": cycle.turbine.SP,
               }
                # use this excel function to convert a table into rows
                # =FILTERXML( "<t><s>" & SUBSTITUTE( MID(AY2,2,LEN(AY2)-2), ",", "</s><s>" ) & "</s></t>", "//s" )

    return results


        