from FluidProperties.fluid import Fluid
import Simulator
from Simulator.streams import MaterialStream


T_geo_in = 200 + 273.15  # K
Q_geo_in = 0.2  # -

T_cool_in = 298  # K
P_cool_in = 101325  # Pa

P_cond = 0.1e5  # Pa
T_cond = 30 + 273.15  # K

geo_in = Fluid(["water", 1])
geo_in = MaterialStream(geo_in, m=1)
geo_in.update("TQ", T_geo_in, Q_geo_in)

cool_in = Fluid(["water", 1])
cool_in = MaterialStream(cool_in, m=100)
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
net_work *= 1e-3
net_power_elec = turbine.power_elec + pump.power_elec
net_power_elec *= 1e-3
pinch = cond.min_deltaT

as_work = -128.575609 + 0.365115521
as_power_elec = -122.146829 + 0.384332128
as_pinch = 5.14999962

print("Work: Aspen {} Power Cycle {} Diff {}".format(as_work, net_work, 100*(as_work-net_work)/as_work))
print("Power_elec: Aspen {} Power Cycle {} Diff {}".format(as_power_elec, net_power_elec, 100*(as_power_elec-net_power_elec)/as_power_elec))
print("Pinch: Aspen {} Power Cycle {} Diff {}".format(as_pinch, pinch, 100*(as_pinch-pinch)/as_pinch))
