import math

import CoolProp as cp
from CoolProp.CoolProp import PropsSI
import matplotlib.pyplot as plt
import numpy as np
import tikzplotlib

water = cp.AbstractState("?", "water")
# water.build_phase_envelope("PH")
# tab_water = water.get_phase_envelope_data()

Tin = 180 + 273.15
Qin = 0.15

Pcond = 0.1e5

water.update(cp.QT_INPUTS, Qin, Tin)
Pin = water.p()
Hin = water.hmass()

water.update(cp.PQ_INPUTS, Pcond, 0.5)
Tcond = water.T()

Tflashs = np.linspace(Tin, Tcond, 20)
Pflashs = [PropsSI("P", "T", t, "Q", 0.5, "water") for t in Tflashs]
Works = []
Xs = []
Powers = []

eta = 0.85
for Pflash in Pflashs:

    water.update(cp.HmassP_INPUTS, Hin, Pflash)
    x = water.Q()
    Xs.append(x)

    water.update(cp.PQ_INPUTS, Pflash, 1)
    Hvap = water.hmass()
    Svap = water.smass()

    water.update(cp.PSmass_INPUTS, Pcond, Svap)
    Hout_isen = water.hmass()

    work = eta*(Hvap-Hout_isen)/1000
    Works.append(work)

    power = x * work
    Powers.append(power)

max_power = max(Powers)
ipwr = Powers.index(max_power)
Topt = Tflashs[ipwr]


fig, axs = plt.subplots(ncols=2)

axs[0].plot(Tflashs, Xs, label="Vapour Quality")
axs[0].plot([297], [-0.1], label="Enthalpy Change", color="#ff7f0e")
axs[0].set_xlabel("Flash Temperature/\\unit{\\K}")
axs[0].set_ylabel("Vapour Quality")
axs[0].set_xlim([300, 480])
axs[0].set_ylim([0, 0.4])
axs[0].legend()

ax_twin = axs[0].twinx()
ax_twin.plot(Tflashs, Works, color="#ff7f0e")
ax_twin.set_xlabel("Flash Temperature/\\unit{\\K}")
ax_twin.set_ylabel("Enthalpy Change/\\unit{\\kilo\\watt\\per\\kg}")
ax_twin.set_xlim([300, 480])
ax_twin.set_ylim([0, 650])

axs[1].plot(Tflashs, Powers)
axs[1].plot([Topt, Topt], [0, max_power], "k:")
axs[1].plot([Topt], [max_power], "ko")
axs[1].set_xlabel("Flash Temperature/\\unit{\\K}")
axs[1].set_ylabel("Turbine Power/\\unit{\\kilo\\watt}")
axs[1].set_xlim([300, 480])
axs[1].set_ylim([0, 110])

tikzplotlib.save("FlashTemperatureOptimisation.tex")

plt.show()


