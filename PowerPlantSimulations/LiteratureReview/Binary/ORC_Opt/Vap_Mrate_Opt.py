import CoolProp as cp
import matplotlib.pyplot as plt
import numpy as np
from CoolProp.CoolProp import PropsSI
import math
import tikzplotlib

Tref = 298
Pref = 101325
rho0_wat = PropsSI("Dmolar", "T", Tref, "P", Pref, "water")
cp.CoolProp.set_reference_state("water", Tref, rho0_wat, 0, 0)
water = cp.AbstractState("?", "water")

T_geo_in = 160 + 273
Q_geo_in = 0

water.update(cp.QT_INPUTS, Q_geo_in, T_geo_in)
P_geo_in_sat = water.p()
H_geo_in = water.hmass()

P_geo_SH = P_geo_in_sat
P_geo_crit = 1e5

WHPs = np.linspace(P_geo_crit, P_geo_SH, 20)
WHPs_bar = [p*1e-5 for p in WHPs]

mrate = [math.sqrt(1- (p/(P_geo_SH))**2) for p in WHPs]

T_geo_ins = [PropsSI("T", "H", H_geo_in, "P", whp, "water") for whp in WHPs]

fig, axs = plt.subplots(ncols=2)

axs[0].plot(WHPs_bar, mrate)
axs[0].set_xlabel("Wellhead Pressure/\\unit{\\bar}")
axs[0].set_ylabel("Mass Rate Ratio/\\unit{\\bar}")

axs[1].plot(WHPs_bar, T_geo_ins)
axs[1].set_xlabel("Wellhead Pressure/\\unit{\\bar}")
axs[1].set_ylabel("Temperature/\\unit{\\K}")
axs[1].set_ylim(300, 450)

tikzplotlib.save("Vap_Mrate_Opt.tex")




