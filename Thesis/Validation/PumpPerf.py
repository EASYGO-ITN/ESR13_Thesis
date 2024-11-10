from FluidProperties.fluid import Fluid
import Simulator
from Simulator.streams import MaterialStream

Pin = 1e5  # Pa
Tin = 298  # K

Pout = 10e5  # Pa

water = Fluid(["water", 1])
water = MaterialStream(water, m=1)
water.update("PT", Pin, Tin)

pump = Simulator.pump(0.85, mech_eff=0.95)
pump.set_inputs(water, Pout)
water_out = pump.calc()

as_work = 1.06191788
as_power_elec = 1.11780829
as_Tout = 298.05465979999997


print("Tout: PowerCycle {:.2f} AspenPlus {:.2f} Difference {:.2f}".format(water_out.properties.T, as_Tout, 100*(as_Tout-water_out.properties.T)/as_Tout))
print("Work: PowerCycle {:.4f} AspenPlus {:.4f} Difference {:.2f}".format(pump.work/1000, as_work, 100*(as_work-pump.work/1000)/as_work))
print("Power: PowerCycle {:.4f} AspenPlus {:.4f} Difference {:.2f}".format(pump.power_elec/1000, as_power_elec, 100*(as_power_elec-pump.power_elec/1000)/as_power_elec))


