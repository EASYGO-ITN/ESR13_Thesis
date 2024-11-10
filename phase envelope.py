import CoolProp as cp
from CoolProp.CoolProp import PropsSI
import matplotlib.pyplot as plt
import numpy as np

import SP2009

water = cp.AbstractState("?", "water")
water.build_phase_envelope("PT")
water_tab = water.get_phase_envelope_data()

ps = np.array(water_tab.p)*1e-5
ts = np.array(water_tab.T)

plt.plot(ts, ps)
plt.plot(water.T_critical(), water.p_critical()*1e-5, "*")

tmin = SP2009.SpycherPruss2009.Tmin_low
tmax = SP2009.SpycherPruss2009.Tmax_high

pmin = SP2009.SpycherPruss2009.Pmin*1e-5
pmax = SP2009.SpycherPruss2009.Pmax*1e-5
pcrit = water.p_critical()*1e-5

SP_bd_p = [pmin, pmin, pmax, pmax, pmin]
SP_bd_t = [tmin, tmax, tmax, tmin, tmin]
plt.plot(SP_bd_t, SP_bd_p, "k")

# psat curve between 1 bar and 12-300°C
ts = np.sort(ts)
ps = np.sort(ps)

psat_bd = ps[tmin<= ts]
tsat_bd = ts[tmin <= ts]
psat_bd = psat_bd[tmax >= tsat_bd]
tsat_bd = tsat_bd[tmax >= tsat_bd]
tsat_bd = tsat_bd[pmin<=psat_bd]
psat_bd = psat_bd[pmin<=psat_bd]

psat_bd = [pmin, pmin] + [p for p in psat_bd]
tsat_bd = [tmin, PropsSI("T", "P", pmin*1e5, "Q", 0, "water")] + [t for t in tsat_bd]
sp_pmin = [pmin for t in tsat_bd]
sp_pmax = [pmax for t in tsat_bd]
sp_pcrit = [pcrit for t in tsat_bd]

plt.fill_between(tsat_bd, sp_pcrit, sp_pmax, color="red", alpha=0.5)
plt.fill_between(tsat_bd, psat_bd, sp_pcrit, color="orange", alpha=0.5)
plt.fill_between(tsat_bd, sp_pmin, psat_bd, color="green", alpha=0.5)

plt.xlabel("Temperature, K")
plt.ylabel("Pressure, bar")
plt.yscale("log")

plt.show()