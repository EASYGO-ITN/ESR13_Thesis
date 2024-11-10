import Simulator
from Simulator.streams import MaterialStream
from FluidProperties.fluid import Fluid

inlet = Fluid(["carbondioxide", 1])
inlet = MaterialStream(inlet, m=1)
inlet.update("PT", Pin, Tin)

compressor = Simulator.multistage_compression(0.85, 1, mech_eff=0.95)
compressor.set_inputs(inlet, Pout, findN=True)
outlet = compressor.calc()