import CoolProp as cp
from CoolProp.CoolProp import PropsSI
import matplotlib.pyplot as plt
import numpy as np
import tikzplotlib

colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]

Tref = 298
Pref = 101325


rho0 = PropsSI("Dmolar", "T", Tref, "Q", 0, "butane")
cp.CoolProp.set_reference_state("butane", Tref, rho0, 0, 0)
butane = cp.AbstractState("?", "butane")

butane.build_phase_envelope("TS")
butane_tab = butane.get_phase_envelope_data()
butane_Mr = butane.molar_mass()

butane_ss = [s*butane_Mr for s in butane_tab.smolar_vap]
butane_ts = butane_tab.T


rho0 = PropsSI("Dmolar", "T", Tref, "Q", 0, "R152a")
cp.CoolProp.set_reference_state("R152a", Tref, rho0, 0, 0)
R152a = cp.AbstractState("?", "R152a")


R152a.build_phase_envelope("TS")
R152a_tab = R152a.get_phase_envelope_data()
R152a_Mr = R152a.molar_mass()

R152a_ss = [s*R152a_Mr for s in R152a_tab.smolar_vap]
R152a_ts = R152a_tab.T


rho0 = PropsSI("Dmolar", "T", Tref, "Q", 0, "R124")
cp.CoolProp.set_reference_state("R124", Tref, rho0, 0, 0)
R124 = cp.AbstractState("?", "R124")


R124.build_phase_envelope("TS")
R124_tab = R124.get_phase_envelope_data()
R124_Mr = R124.molar_mass()

R124_ss = [s*R124_Mr for s in R124_tab.smolar_vap]
R124_ts = R124_tab.T

fig, ax = plt.subplots(ncols=3)

ax[0].plot(butane_ss, butane_ts, label="n-Butane")
ax[0].set_ylim(273, 500)

ax[1].plot(R124_ss, R124_ts, label="R124")
ax[2].plot(R152a_ss, R152a_ts, label="R152a")

ax[0].legend()
ax[1].legend()
ax[2].legend()
plt.show()
