from FluidProperties.fluid import Fluid
import Simulator
from Simulator.streams import MaterialStream

T_geo_in = 180 + 273.15  # K
Q_geo_in = 0  # -
m_geo = 1  # kg/s

T_cool_in = 298  # K
P_cool_in = 101325  # Pa
m_cool = 100  # kg/s

P_evap = 20e5  # Pa
Q_evap = 1  # -

P_cond = 3e5  # Pa
Q_cond = 0  # -

m_wf = 1  # kg/s


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
net_work *= 1e-3
net_power_elec = turbine.power_elec + pump.power_elec
net_power_elec *= 1e-3
pinch_PHE = PHE.min_deltaT
pinch_cond = cond.min_deltaT

as_work = -66.7273331 + 3.54158047
as_power_elec = -63.3909664	+ 3.72797944
as_pinch_PHE = 13.6006434
as_pinch_cond = 6.06553827

print("Work: Aspen {} Power Cycle {} Diff {}".format(as_work, net_work, 100*(as_work-net_work)/as_work))
print("Power_elec: Aspen {} Power Cycle {} Diff {}".format(as_power_elec, net_power_elec, 100*(as_power_elec-net_power_elec)/as_power_elec))
print("Pinch_PHE: Aspen {} Power Cycle {} Diff {}".format(as_pinch_PHE, pinch_PHE, 100*(as_pinch_PHE - pinch_PHE)/as_pinch_PHE))
print("Pinch_cond: Aspen {} Power Cycle {} Diff {}".format(as_pinch_cond, pinch_cond, 100*(as_pinch_cond - pinch_cond)/as_pinch_cond))

# sanity check
print("Sanity Check")
print(wf_pump_in.properties.T - wf_pump_in_.properties.T)
print(wf_pump_in.properties.P - wf_pump_in_.properties.P)