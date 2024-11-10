from FluidProperties.fluid import Fluid
import Simulator
from Simulator.streams import MaterialStream

geo_in = Fluid(["water", 1])
geo_in = MaterialStream(geo_in, m=m_geo)
geo_in.update("TQ", T_geo_in, Q_geo_in)

cool_in = Fluid(["water", 1])
cool_in = MaterialStream(cool_in, m=m_cool)
cool_in.update("PT", P_cool_in, T_cool_in)

sep = Simulator.separator()
sep.set_inputs(geo_in)
liq, vap = sep.calc()

turbine = Simulator.turbine(0.85, mech_eff=0.95)
turbine.set_inputs(vap, P_cond)
vap = turbine.calc()

condensate_ = vap.copy()
condensate_.update("PT", P_cond, T_cond)

cond = Simulator.heat_exchanger(deltaP_hot=0, deltaP_cold=0)
cond.set_inputs(Inlet_hot=vap, Inlet_cold=cool_in, Outlet_hot=condensate_)
condensate, cool_out = cond.calc()

pump = Simulator.pump(0.85, mech_eff=0.95)
pump.set_inputs(condensate, geo_in.properties.P)
condensate = pump.calc()

mixer = Simulator.mixer()
mixer.set_inputs(liq, condensate)
geo_out = mixer.calc()

net_work = turbine.work + pump.work
net_power_elec = turbine.power_elec + pump.power_elec