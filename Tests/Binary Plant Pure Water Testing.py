from FluidProperties.fluid import Fluid
from Simulator.streams import MaterialStream

import time

T_inlet = 448.15
Q_inlet = 0.5

geofluid = Fluid(["water", 1], engine="default")
geofluid_stream = MaterialStream(geofluid, m=1)
geofluid_stream.update("TQ", T_inlet, Q_inlet)

coolant = Fluid(["air", 1])
coolant_stream = MaterialStream(coolant, m=1)

workingfluid = Fluid(["nButane", 1])
workingfluid_stream = MaterialStream(workingfluid, m=1)

Pmax = 2.7e6
Tmax = 141 + 273.15
Tmin = 303
Pmin = 5e5

Pcrit = workingfluid.state.state.state.p_critical()

# simple binary ORC with a H2O geofluid
if __name__ == "__main_":

    from Simulator.BinaryCycles.simple_binary import ORC as simpleORC

    orc = simpleORC(recu=False)

    orc.set_geofluid(geofluid_stream.copy())
    orc.set_coolant(coolant_stream.copy())
    orc.set_workingfluid(workingfluid_stream.copy())

    orc.condenser.deltaP_cold = 10000

    net_power = orc.calc(0.518*Pcrit, 392, 303.1)
    eff_1st_law = orc.first_law_efficiency()
    eff_2nd_law = orc.second_law_efficiency()

    print("\nSimple ORC")
    print("    -------------------    ")
    print(" NetPow: {:8.2f} kW".format(net_power/1e3))
    print("EnergyBal: {:8.2e} kW".format(orc.energy_balance/1e3))
    print("eta_1st: {:8.2f} %".format(eff_1st_law*100))
    print("eta_2nd: {:8.2f} %".format(eff_2nd_law*100))
    print("    -------------------    ")
    print("   M_wf: {:8.2f} kg/s".format(orc.wfluid.m))
    print(" M_cool: {:8.2f} kg/s".format(orc.coolant.m))
    print("    -------------------    ")
    # print("Recu DT: {:8.2f} K".format(orc.recuperator.min_deltaT))
    print("PreH DT: {:8.2f} K".format(orc.preheater.min_deltaT))
    print("Evap DT: {:8.2f} K".format(orc.evaporator.min_deltaT))
    print("Cond DT: {:8.2f} K".format(orc.condenser.min_deltaT))

    #
    orc.plot_TQ()
    orc.plot_TS()

# series binary ORC with a H2O geofluid and tertiary fluid for heat transfer
if __name__ == "__main__":

    from Simulator.BinaryCycles.simple_binary_tertiary import ORC as simpleORC_tertiary

    tertiaryfluid = Fluid(["water", 1])
    tertiaryfluid_stream = MaterialStream(tertiaryfluid, m=1)

    # simple_cycle = tORC()
    orc = simpleORC_tertiary(recu=False)

    orc.set_geofluid(geofluid_stream)
    orc.set_coolant(coolant_stream.copy())
    orc.set_workingfluid(workingfluid_stream.copy())
    orc.set_tertiaryfluid(tertiaryfluid_stream.copy())

    loc_Pmax = 4e6
    loc_Tmax = 160 + 273.15
    loc_Tmin = 350

    net_power = orc.calc(loc_Pmax, loc_Tmax, loc_Tmin)
    eff_1st_law = orc.first_law_efficiency()
    eff_2nd_law = orc.second_law_efficiency()

    print("\nSeries ORC with tertiary fluid")
    print(" NetPow: {:8.2f} kW".format(net_power/1e3))
    print("EnergyBal: {:8.2e} kW".format(orc.energy_balance/1e3))
    print("eta_1st: {:8.2f} %".format(eff_1st_law*100))
    print("eta_2nd: {:8.2f} %".format(eff_2nd_law*100))
    print("    -------------------    ")
    print("   M_wf: {:8.2f} kg/s".format(orc.wfluid.m))
    print(" M_cool: {:8.2f} kg/s".format(orc.coolant.m))
    print(" M_tert: {:8.2f} kg/s".format(orc.tfluid.m))
    print("    -------------------    ")
    print("Recu DT: {:8.2f} K".format(orc.recuperator.min_deltaT))
    print("PreH DT: {:8.2f} K".format(orc.preheater.min_deltaT))
    print("Evap DT: {:8.2f} K".format(orc.evaporator.min_deltaT))
    print("GeoC DT: {:8.2f} K".format(orc.geo_condenser.min_deltaT))
    print("Cond DT: {:8.2f} K".format(orc.condenser.min_deltaT))

    orc.plot_TQ()
    orc.plot_TS()


# series binary ORC with a H2O geofluid
if __name__ == "__main_":

    from Simulator.BinaryCycles.series_binary import ORC as seriesORC

    orc = seriesORC(recu=True)

    orc.set_geofluid(geofluid_stream.copy())
    orc.set_coolant(coolant_stream.copy())
    orc.set_workingfluid(workingfluid_stream.copy())

    net_power = orc.calc(0.387777*Pcrit, 400, 303.01)
    eff_1st_law = orc.first_law_efficiency()
    eff_2nd_law = orc.second_law_efficiency()

    print("\nSeries ORC")
    print(" NetPow: {:8.2f} kW".format(net_power/1e3))
    print("EnergyBal: {:8.2e} kW".format(orc.energy_balance/1e3))
    print("eta_1st: {:8.2f} %".format(eff_1st_law*100))
    print("eta_2nd: {:8.2f} %".format(eff_2nd_law*100))
    print("    -------------------    ")
    print("   M_wf: {:8.2f} kg/s".format(orc.wfluid.m))
    print(" M_cool: {:8.2f} kg/s".format(orc.coolant.m))
    print("    -------------------    ")
    print("Recu DT: {:8.2f} K".format(orc.recuperator.min_deltaT))
    print("PreH DT: {:8.2f} K".format(orc.preheater.min_deltaT))
    print("Evap DT: {:8.2f} K".format(orc.evaporator.min_deltaT))
    print("Cond DT: {:8.2f} K".format(orc.condenser.min_deltaT))

    orc.plot_TQ()
    orc.plot_TS()

# series binary ORC with a H2O geofluid and condensate reuse
if __name__ == "__main_":

    from Simulator.BinaryCycles.reuse_condensate_binary import ORC as seriesORC_reuse_cond

    # orc = seriesORC_reuse_cond()
    orc = seriesORC_reuse_cond(recu=True)

    orc.deltaT_superheat = 2
    orc.condenser.deltaP_cold = 120
    orc.coolingpump.eta_isentropic = 0.6

    orc.set_geofluid(geofluid_stream.copy())
    orc.set_coolant(coolant_stream.copy())
    orc.set_workingfluid(workingfluid_stream.copy())

    net_power = orc.calc(0.451755583*Pcrit, 385, 306.91)
    eff_1st_law = orc.first_law_efficiency()
    eff_2nd_law = orc.second_law_efficiency()

    print("\nseries ORC with condensate recycling")
    print(" NetPow: {:8.2f} kW".format(net_power/1e3))
    print(" CyclePow: {:8.2f} kW".format(orc.cycle_power / 1e3))
    print(" ParasiticPow : {:8.2f} kW".format(orc.parasitic_power / 1e3))

    print("EnergyBal: {:8.2e} kW".format(orc.energy_balance/1e3))
    print("eta_1st: {:8.2f} %".format(eff_1st_law*100))
    print("eta_2nd: {:8.2f} %".format(eff_2nd_law*100))
    print("    -------------------    ")
    print("   M_wf: {:8.2f} kg/s".format(orc.wfluid.m))
    print(" M_cool: {:8.2f} kg/s".format(orc.coolant.m))
    print("    -------------------    ")
    print("Recu DT: {:8.2f} K".format(orc.recuperator.min_deltaT))
    print("PreH DT: {:8.2f} K".format(orc.preheater.min_deltaT))
    print("Evap DT: {:8.2f} K".format(orc.evaporator.min_deltaT))
    print("Cond DT: {:8.2f} K".format(orc.condenser.min_deltaT))

    orc.plot_TQ()
    orc.plot_TS()

# parallel ORC with a H2O geofluid
if __name__ == "__main_":

    from Simulator.BinaryCycles.parallel_binary import ORC as parallelORC

    # orc = parallelORC()
    orc = parallelORC(recu=True)

    orc.set_geofluid(geofluid_stream.copy())
    orc.set_coolant(coolant_stream.copy())
    orc.set_workingfluid(workingfluid_stream.copy())

    net_power = orc.calc(0.7800095818198407*Pcrit, 415.1224326331528, 303.0205088)
    eff_1st_law = orc.first_law_efficiency()
    eff_2nd_law = orc.second_law_efficiency()

    print("\nparallel ORC")
    print(" NetPow: {:8.2f} kW".format(net_power/1e3))
    print("EnergyBal: {:8.2e} kW".format(orc.energy_balance/1e3))
    print("eta_1st: {:8.2f} %".format(eff_1st_law*100))
    print("eta_2nd: {:8.2f} %".format(eff_2nd_law*100))
    print("    -------------------    ")
    print("   M_wf: {:8.2f} kg/s".format(orc.wfluid.m))
    print(" M_cool: {:8.2f} kg/s".format(orc.coolant.m))
    print("    -------------------    ")
    print("Recu DT: {:8.2f} K".format(orc.recuperator.min_deltaT))
    print("SPreH DT: {:8.2f} K".format(orc.vapour_preheater.min_deltaT))
    print("SEvap DT: {:8.2f} K".format(orc.vapour_evaporator.min_deltaT))
    print("BPreH DT: {:8.2f} K".format(orc.brine_preheater.min_deltaT))
    print("BEvap DT: {:8.2f} K".format(orc.brine_evaporator.min_deltaT))
    print("Cond DT: {:8.2f} K".format(orc.condenser.min_deltaT))
    #
    orc.plot_TQ()
    orc.plot_TS()

# parallel ORC with a H2O geofluid and dual pressure
if __name__ == "__main_":

    from Simulator.BinaryCycles.parallel_binary_dual_pressure import ORC as parallelORC_dualP

    HPmax = 3.6e6
    HTmax = 160 + 273.15
    Pmin = 5e5

    # orc = parallelORC_dualP()
    orc = parallelORC_dualP(recu=True)

    orc.set_geofluid(geofluid_stream.copy())
    orc.set_coolant(coolant_stream.copy())
    orc.set_workingfluid(workingfluid_stream.copy())

    net_power = orc.calc(4722330.975, 462.4939503, 3220193.533, 443.5786913, 303.217)
    eff_1st_law = orc.first_law_efficiency()
    eff_2nd_law = orc.second_law_efficiency()

    print("\nparallel ORC with dual pressure")
    print(" NetPow: {:8.2f} kW".format(net_power/1e3))
    print("EnergyBal: {:8.2e} kW".format(orc.energy_balance/1e3))
    print("eta_1st: {:8.2f} %".format(eff_1st_law*100))
    print("eta_2nd: {:8.2f} %".format(eff_2nd_law*100))
    print("    -------------------    ")
    print("   M_wf: {:8.2f} kg/s".format(orc.wfluid.m))
    print(" M_cool: {:8.2f} kg/s".format(orc.coolant.m))
    print("    -------------------    ")
    print("Recu DT: {:8.2f} K".format(orc.recuperator.min_deltaT))
    print("SPreH DT: {:8.2f} K".format(orc.vapour_preheater.min_deltaT))
    print("SEvap DT: {:8.2f} K".format(orc.vapour_evaporator.min_deltaT))
    print("BPreH DT: {:8.2f} K".format(orc.brine_preheater.min_deltaT))
    print("BEvap DT: {:8.2f} K".format(orc.brine_evaporator.min_deltaT))
    print("Cond DT: {:8.2f} K".format(orc.condenser.min_deltaT))

    orc.plot_TQ()
    orc.plot_TS()

# parallel ORC with a H2O geofluid and dual fluid
if __name__ == "__main_":

    from Simulator.BinaryCycles.parallel_binary_dual_fluid import ORC as parallelORC_dualFluid

    VPmax = 1.9e6
    VTmax = 168 + 273.15
    VPmin = 1e5
    VTmin = 303

    workingfluid_B = Fluid(["nPentane", 1])
    workingfluid_stream_B = MaterialStream(workingfluid_B, m=1)

    # orc = parallelORC_dualFluid()
    orc = parallelORC_dualFluid(recu=True)

    orc.set_geofluid(geofluid_stream.copy())
    orc.set_coolant(coolant_stream.copy())
    orc.set_workingfluid(workingfluid_stream.copy(), workingfluid_stream_B.copy())

    net_power = orc.calc(Pmax, Tmax, Tmin, VPmax, VTmax, VTmin, VP_min=VPmin, BP_min=Pmin)
    eff_1st_law = orc.first_law_efficiency()
    eff_2nd_law = orc.second_law_efficiency()

    print("\nparallelORC with dual fluid")
    print("  NetPow: {:8.2f} kW".format(net_power/1e3))
    print("EnergyBal: {:8.2e} kW".format(orc.energy_balance/1e3))
    print(" eta_1st: {:8.2f} %".format(eff_1st_law*100))
    print(" eta_2nd: {:8.2f} %".format(eff_2nd_law*100))
    print("    -------------------    ")
    print("NetPow_V: {:8.2f} kW".format(orc.vapour_ORC.net_power/1e3))
    print("EnergyBal: {:8.2e} kW".format(orc.vapour_ORC.energy_balance/1e3))
    print("NetPow_B: {:8.2f} kW".format(orc.brine_ORC.net_power/1e3))
    print("EnergyBal: {:8.2e} kW".format(orc.brine_ORC.energy_balance/1e3))
    print("    -------------------    ")
    print("  M_wf_V: {:8.2f} kg/s".format(orc.wfluidV.m))
    print("  M_wf_B: {:8.2f} kg/s".format(orc.wfluidB.m))
    print("  M_cool: {:8.2f} kg/s".format(orc.coolant.m))
    print("    --- BrineBranch ---    ")
    print(" Recu DT: {:8.2f} K".format(orc.brine_ORC.recuperator.min_deltaT))
    print(" PreH DT: {:8.2f} K".format(orc.brine_ORC.preheater.min_deltaT))
    print(" Evap DT: {:8.2f} K".format(orc.brine_ORC.evaporator.min_deltaT))
    print(" Cond DT: {:8.2f} K".format(orc.brine_ORC.condenser.min_deltaT))
    print("    -- VapourBranch ---    ")
    print(" Recu DT: {:8.2f} K".format(orc.vapour_ORC.recuperator.min_deltaT))
    print(" PreH DT: {:8.2f} K".format(orc.vapour_ORC.preheater.min_deltaT))
    print(" Evap DT: {:8.2f} K".format(orc.vapour_ORC.evaporator.min_deltaT))
    print(" Cond DT: {:8.2f} K".format(orc.vapour_ORC.condenser.min_deltaT))


    orc.plot_TQ()
    orc.plot_TS()


