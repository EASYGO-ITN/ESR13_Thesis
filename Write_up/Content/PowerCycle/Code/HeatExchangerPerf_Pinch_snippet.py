import Simulator
from Simulator.streams import MaterialStream
from FluidProperties.fluid import Fluid

hot_in = Fluid(["water", 1])
hot_in = MaterialStream(hot, m=1)
hot_in.update("TQ", Tin_H, Qin_H)

cold_in = Fluid(["butane", 1])
cold_in = MaterialStream(cold_in, m=1)
cold_in = cold_in.update("PT", Pin_C, T_in_C)

cold_out = cold_in.copy()
cold_out.update("PQ", Pin_C, 1)
Tsat_C = cold_out.properties.T
cold_out.update("PT", Pin_C, Tsat_C + 10)

HX = Simulator.heat_exchanger(deltaP_hot=0, deltaP_cold=0)
HX.set_inputs(MassRatio=-1, Inlet_hot=hot_in, Inlet_cold=cold_in, Outlet_cold=cold_out)
hot_out, cold_out = HX.calc()