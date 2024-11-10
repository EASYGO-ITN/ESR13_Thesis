import Simulator
from Simulator.streams import MaterialStream
from FluidProperties.fluid import Fluid

inlet = Fluid(["carbondioxide", 1])
inlet = MaterialStream(inlet, m=1)
inlet.update("PT", Pin, Tin)

compressor = Simulator.pump(0.85, mech_eff=0.95)
compressor.set_inputs(inlet, Pout)
outlet = compressor.calc()