import CoolProp as cp
import numpy as np
from CoolProp.CoolProp import PropsSI
import matplotlib.pyplot as plt
from copy import deepcopy

Pref = 101325
Tref = 298

# set the new reference conditions
wat_rho = PropsSI("Dmolar",  "P", Pref, "T", Tref, "Water")
# cp.CoolProp.set_reference_state('Water', Tref, wat_rho, 0, 0)

air = cp.AbstractState("?", "CO2")
water = cp.AbstractState("?", "water")
water.build_phase_envelope("TS")
tab_water = water.get_phase_envelope_data()

Tboil = 315  # K
Tcond = 298
Pevap = PropsSI("P", "T", Tboil, "Q", 1, "Water")
Pcond = PropsSI("P", "T", Tcond, "Q", 1, "Water")

states = [cp.AbstractState("?", "Water") for i in range(7)]
states[0].update(cp.PQ_INPUTS, Pcond, 0)  # initial
states[1].update(cp.PSmolar_INPUTS, Pevap, states[0].smolar())  # pump outlet
states[2].update(cp.PQ_INPUTS, Pevap, 0)
states[3].update(cp.PQ_INPUTS, Pevap, 1)
states[5].update(cp.PQ_INPUTS, Pcond, 1)
states[4].update(cp.PSmolar_INPUTS, Pevap, states[5].smolar())
states[6].update(cp.PQ_INPUTS, Pcond, 0)  # initial

fig, axs = plt.subplots(ncols=2)

ss = [i.smass()/1000 for i in states]
ts = [i.T() for i in states]
axs[0].plot(np.array(tab_water.smolar_vap)/0.018/1000, tab_water.T, "k:", label="Phase Envelope", )
axs[0].plot(ss, ts, "g.-", label="Cycle")
axs[0].set_xlabel("Entropy, kJ/kg/K")
axs[0].set_ylabel("Temperature, K")
axs[0].set_xlim([0, None])
axs[0].set_ylim([Tref-25, None])

N_preh = 10
N_suph = 20
h0 = PropsSI("H", "P", Pevap, "Smolar", states[1].smolar(), "Water")

whs = [(PropsSI("H", "P", Pevap, "Smolar", s, "Water")-h0)/1000 for s in list(np.linspace(states[1].smolar(), states[2].smolar(), N_preh))]\
     +[(PropsSI("H", "P", Pevap, "Smolar", s, "Water")-h0)/1000 for s in list(np.linspace(states[3].smolar(), states[4].smolar(), N_suph))]
whts = [PropsSI("T", "P", Pevap, "Smolar", s, "Water") for s in list(np.linspace(states[1].smolar(), states[2].smolar(), N_preh))]\
     +[PropsSI("T", "P", Pevap, "Smolar", s, "Water") for s in list(np.linspace(states[3].smolar(), states[4].smolar(), N_suph))]

DeltaH = (states[4].hmass() - states[0].hmass())
DeltaHsat = (states[4].hmass() - states[2].hmass())


Tin = states[4].T()+10
Tsat = states[3].T()+10
Pair = 3e5
Hinc = PropsSI("H", "P", Pair, "T", Tin, "CO2")
Hsatc = PropsSI("H", "P", Pair, "T", Tsat, "CO2")
DeltaHsatc = Hinc - Hsatc

nc = DeltaHsat / DeltaHsatc
hsc = np.linspace(0, DeltaH, 30)
tsc = [PropsSI("T", "H", Hinc - h/nc, "P", Pair, "CO2") for h in hsc]
hsc = whs[-1] - hsc/1000

axs[1].plot([(i/0.018-h0)/1000 for i in tab_water.hmolar_liq], tab_water.T, "k:", label="Phase Envelope")
axs[1].plot(whs, whts, "g", label="Working Fluid")
axs[1].plot(hsc, tsc, "r", label="Heat Source")
axs[1].set_xlabel("Heat Transferred, J/mol")
axs[1].set_ylabel("Temperature, K")
axs[1].set_xlim([0, DeltaH/1000])
axs[1].set_ylim([Tcond, Tin+25])

fig.tight_layout()
plt.show()
