import Simulator
from Simulator.streams import MaterialStream
from FluidProperties.fluid import Fluid

inlet = Fluid(["water", 1])
inlet = MaterialStream(inlet, m=1)
inlet.update("TQ", Tin, Qin)

pump = Simulator.turbine(0.85, mech_eff=0.95)
pump.set_inputs(inlet, Pout)
outlet = pump.calc()