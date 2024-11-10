import math
import CoolProp as cp

from time import perf_counter
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np


def to_tex3D(xs, ys, zs):

    # xys = ["({:.3e},{:.3e}) [:.e3]".format(xs[i],ys[j], zs[i][j]) for i in range(len(xs) for j in range(len(ys))]
    xyzs = ["({:.3e},{:.3e}) [{}]".format(ys[j], xs[i], int(zs[i][j])) for j in range(len(ys)) for i in range(len(xs))]
    coords = " ".join(xyzs)

    return coords


def to_tex3D_binary_map(xs, ys, zs, color0, color1):

    coords = []
    for i, x in enumerate(xs):

        vals = []
        for j, y in enumerate(ys):
            if zs[i][j] < 0.5:
                color = color0
            else:
                color = color1

            vals.append("({:.3e},{:.3e}) [color={}]".format(y,x,color))
        vals.append("\n\n")
        coords.append(" ".join(vals))

    return "".join(coords)

ps_bar = [1, 300]  # set the minimum and maximum pressure in bar
N_p = 30 #40  # the number of pressure steps

ts_c = [25, 300]  # set the minimum and maximum temperature in °C
N_t = 60 #88  # the number of temperature steps

Ts = np.linspace(ts_c[0], ts_c[1], N_t) + 273.15
Ps = np.logspace(math.log10(ps_bar[0]), math.log10(ps_bar[1]), N_p) * 1e5

# zs = [0.0, 0.005, 0.01, 0.02, 0.05, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 0.98, 0.99, 0.995, 1.0]
zs = [0.0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
N_z = len(zs)
Zs = np.array(zs)

state = cp.AbstractState("?", "Water&CarbonDioxide")
for i, z in enumerate(Zs):

    calc_map = np.ones((N_p, N_t))
    state.set_mole_fractions([1 - z, z])

    for j, p in enumerate(Ps):
        for k, t in enumerate(Ts):
            try:
                state.update(cp.PT_INPUTS, p, t)
            except:
                calc_map[j][k] = 0

    print("ZCO2 {}".format(z))
    # print(to_tex3D((Ps*1e-5).tolist(), Ts.tolist(), calc_map))

    print(to_tex3D_binary_map((Ps*1e-5).tolist(), Ts.tolist(), calc_map, "red", "blue"))

    



