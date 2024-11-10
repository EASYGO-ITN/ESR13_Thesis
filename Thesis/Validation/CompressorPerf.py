from FluidProperties.fluid import Fluid
import Simulator
from Simulator.streams import MaterialStream

Pin = 0.1e5  # Pa
Tin = 298  # K

Pout = 10e5  # Pa

inlet = Fluid(["carbondioxide", 1])
inlet = MaterialStream(inlet, m=1)
inlet.update("PT", Pin, Tin)

compressor = Simulator.pump(0.85, mech_eff=0.95)
compressor.set_inputs(inlet, Pout)
outlet = compressor.calc()

as_work = 499.530452
as_power_elec = 525.821528
as_Tout = 784.653134573685


print("Tout: PowerCycle {:.2f} AspenPlus {:.2f} Difference {:.2f}".format(outlet.properties.T, as_Tout, 100*(as_Tout-outlet.properties.T)/as_Tout))
print("Work: PowerCycle {:.4f} AspenPlus {:.4f} Difference {:.2f}".format(compressor.work/1000, as_work, 100*(as_work-compressor.work/1000)/as_work))
print("Power: PowerCycle {:.4f} AspenPlus {:.4f} Difference {:.2f}".format(compressor.power_elec/1000, as_power_elec, 100*(as_power_elec-compressor.power_elec/1000)/as_power_elec))


