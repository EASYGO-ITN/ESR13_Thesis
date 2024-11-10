from FluidProperties.fluid import Fluid
import Simulator
from Simulator.streams import MaterialStream

geo_in = Fluid(["water", 1])
geo_in = MaterialStream(geo_in, m=m_geo)
geo_in.update("TQ", T_geo_in, Q_geo_in)

cool_in = Fluid(["water", 1])
cool_in = MaterialStream(cool_in, m=m_cool)
cool_in.update("PT", P_cool_in, T_cool_in)

wf = Fluid(["butane", 1])
wf = MaterialStream(wf, m=m_wf)

wf_pump_in = wf.copy()
wf_pump_in.update("PQ", P_cond, Q_cond)

pump = Simulator.pump(0.85, mech_eff=0.95)
pump.set_inputs(wf_pump_in, P_evap)
wf_PHE_in = pump.calc()

wf_turb_in_ = wf.copy()
wf_turb_in_.update("PQ", P_evap, Q_evap)

PHE = Simulator.heat_exchanger(deltaP_hot=0, deltaP_cold=0, N_discretisation=25)
PHE.set_inputs(Inlet_hot=geo_in, Inlet_cold=wf_PHE_in, Outlet_cold=wf_turb_in_)
geo_out, wf_turb_in = PHE.calc()

turbine = Simulator.turbine(0.85, mech_eff=0.95)
turbine.set_inputs(wf_turb_in, P_cond)
wf_cond_in = turbine.calc()

cond = Simulator.heat_exchanger(deltaP_hot=0, deltaP_cold=0)
cond.set_inputs(Inlet_hot=wf_cond_in, Inlet_cold=cool_in, Outlet_hot=wf_pump_in)
wf_pump_in_, cool_out = cond.calc()

net_work = turbine.work + pump.work
net_power_elec = turbine.power_elec + pump.power_elec