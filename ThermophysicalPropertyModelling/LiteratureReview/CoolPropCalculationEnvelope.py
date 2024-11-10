import math
import CoolProp as cp
from CoolProp.CoolProp import PropsSI

from time import perf_counter
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import tikzplotlib


ps_bar = [1, 300]  # set the minimum and maximum pressure in bar
N_p = 30 #40  # the number of pressure steps

ts_c = [25, 300]  # set the minimum and maximum temperature in °C
N_t = 60 #88  # the number of temperature steps

Ts = np.linspace(ts_c[0], ts_c[1], N_t) + 273.15
Ps = np.logspace(math.log10(ps_bar[0]), math.log10(ps_bar[1]), N_p) * 1e5

ts_wat = []
ps_wat = []
water = cp.AbstractState("?", "water")
for t in Ts:
    water.update(cp.QT_INPUTS, 0, t)
    ps_wat.append(water.p()*1e-5)
    ts_wat.append(t)

ps_co2 = []
ts_co2 = []
co2 = cp.AbstractState("?", "carbondioxide")
for t in Ts:
    if t < co2.T_critical():
        co2.update(cp.QT_INPUTS, 0, t)
        ps_co2.append(co2.p()*1e-5)
        ts_co2.append(t)

state = cp.AbstractState("?", "Water&CarbonDioxide")

zs=[0.0, 0.001, 0.01, 0.1]
N_z = len(zs)
Zs = np.array(zs)

fig, ax = plt.subplots(N_z)
for i, z in enumerate(Zs):

    calc_map = np.ones((N_p, N_t))
    state.set_mole_fractions([1 - z, z])

    ps = []
    ts = []

    for j, p in enumerate(Ps):
        for k, t in enumerate(Ts):
            try:
                state.update(cp.PT_INPUTS, p, t)
            except:
                calc_map[j][k] = 0

                ps.append(p*1e-5)
                ts.append(t)

    if i == 0:
        ax[i].plot(ts, ps, "r.", label="Non-convergence")
        ax[i].plot(ts_wat, ps_wat, "k", label="Sat. curve \\ce{H2O}")
        ax[i].plot(ts_co2, ps_co2, "k--", label="Sat. curve \\ce{CO2}")
    else:
        ax[i].plot(ts, ps, "r.")
        ax[i].plot(ts_wat, ps_wat, "k")
        ax[i].plot(ts_co2, ps_co2, "k--")

    ax[i].set_title("\\(z_{CO_2}=\\)\\qty{"+"{}".format(z*100)+"}{\\mol\\percent}")
    ax[i].set_xlabel("Temperature/\\unit{\\K}")
    ax[i].set_ylabel("Pressure/\\unit{\\bar}")
    ax[i].set_xlim(298, 573)
    ax[i].set_ylim(1, 300)
    ax[i].set_yscale("log")

tikzplotlib.save("CP_CalculationMap.tex")

plt.show()

    # print("ZCO2 {}".format(z))
    # # print(to_tex3D((Ps*1e-5).tolist(), Ts.tolist(), calc_map))
    #
    # print(to_tex3D_binary_map((Ps*1e-5).tolist(), Ts.tolist(), calc_map, "red", "blue"))

    



