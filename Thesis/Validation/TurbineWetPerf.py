from FluidProperties.fluid import Fluid
import Simulator
from Simulator.streams import MaterialStream

Tin = 273.15 + 200  # K
Qin = 1

Pout = 0.1e5  # Pa

water = Fluid(["water", 1])
water = MaterialStream(water, m=1)
water.update("TQ", Tin, Qin)

pump = Simulator.turbine(0.85, mech_eff=0.95, BaumannCorrection=True)
pump.set_inputs(water, Pout)
water_out = pump.calc()

as_work = -591.380059
as_power_elec = -561.811056
as_Tout = 318.9563289
as_Qout = 0.839789442


print("Tout: PowerCycle {:.2f} AspenPlus {:.2f} Difference {:.2f}".format(water_out.properties.T, as_Tout, 100*(as_Tout-water_out.properties.T)/as_Tout))
print("Work: PowerCycle {:.4f} AspenPlus {:.4f} Difference {:.2f}".format(pump.work/1000, as_work, 100*(as_work-pump.work/1000)/as_work))
print("Power: PowerCycle {:.4f} AspenPlus {:.4f} Difference {:.2f}".format(pump.power_elec/1000, as_power_elec, 100*(as_power_elec-pump.power_elec/1000)/as_power_elec))
print("Quality: PowerCycle {:.4f} AspenPlus {:.4f} Difference {:.2f}".format(water_out.properties.Q, as_Qout, 100*(as_Qout-water_out.properties.Q)/as_Qout))
