import math

import CoolProp as cp
from CoolProp.CoolProp import PropsSI
import matplotlib.pyplot as plt
import numpy as np
import tikzplotlib

water = cp.AbstractState("?", "water")
water.build_phase_envelope("PH")
tab_water = water.get_phase_envelope_data()

Mr = 0.018
hmass = [s/Mr for s in tab_water.hmolar_vap]

Tin = 200 + 273
Qin = 1
water.update(cp.QT_INPUTS, Qin, Tin)
Pin = water.p()
Hin = water.hmass()

Pout = 0.1e5
eta = 0.85
whps = np.logspace(math.log10(Pin-1), math.log10(Pout), 50)
work = []
for p in whps:
    water.update(cp.HmassP_INPUTS, Hin, p)
    S = water.smass()

    water.update(cp.PSmass_INPUTS, Pout, S)
    Hisen = water.hmass()

    H = Hin - eta*(Hin - Hisen)
    # water.update(cp.HmassP_INPUTS, H, Pout)

    work.append((Hin - Hisen)/1000)

mrate = [math.sqrt(1- (p/Pin)**2) for p in whps]
power = [mrate[i]*work[i] for i in range(len(whps))]

max_power = max(power)
ipwr = power.index(max_power)
whps = [p*1e-5 for p in whps]
Popt = whps[ipwr]
# ax.plot(hmass, tab_water.p, "k:")


fig, axs = plt.subplots(ncols=2)

axs[0].plot(whps, mrate, label="Mass Rate Ratio")
axs[0].plot([1], [-1], label="Enthalpy Change", color="#ff7f0e")
axs[0].set_xlabel("Pressure/\\unit{\\bar}")
axs[0].set_ylabel("Mass Rate Ratio")
axs[0].set_xlim([0, 16])
axs[0].set_ylim([0, 1.05])
axs[0].legend()

ax_twin = axs[0].twinx()
ax_twin.plot(whps, work, color="#ff7f0e")
ax_twin.set_xlabel("Pressure/\\unit{\\bar}")
ax_twin.set_ylabel("Enthalpy Change/\\unit{\\kilo\\watt\\per\\kg}")
ax_twin.set_xlim([0, 16])
ax_twin.set_ylim([0, 800])

axs[1].plot(whps, power)
axs[1].plot([whps[ipwr], whps[ipwr]], [0, max_power], "k:")
axs[1].plot([whps[ipwr]], [max_power], "ko")
axs[1].set_xlabel("Pressure/\\unit{\\bar}")
axs[1].set_ylabel("Turbine Power/\\unit{\\kilo\\watt}")
axs[1].set_xlim([0, 16])
axs[1].set_ylim([0, 650])

#
# Pcrits = [0, 1e5, 2e5, 4e5, 8e5]
# for Pcrit in Pcrits:
#     mrate_choked = [math.sqrt(1- ((p*1e5-Pcrit)/(Pin-Pcrit))**2) if p*1e5 > Pcrit else 1 for p in whps]
#     power_choked = [mrate_choked[i] * work[i] for i in range(len(whps))]
#
#     axs[3].plot(whps, power_choked)
#     axs[0].plot(whps, mrate_choked)



# tikzplotlib.save("MassRateOptimisation.tex")

plt.show()

