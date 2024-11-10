import numpy as np
from math import exp
import matplotlib.pyplot as plt

N = 50
plt.gca().invert_yaxis()


g = 9.81
rho_brine = 1000
P0_brine = 1e5
H_max = 4000

hs_brine = np.linspace(0, H_max, N)
P_brine = rho_brine*g*hs_brine + P0_brine
plt.plot(P_brine*1e-5, hs_brine, label="Brine")


Mr_co2 = 0.044
R = 8.314
T_co2 = 293

h_injs = [500, 1000, 2000, 4000]
for h in h_injs:
    hs_ncg = np.linspace(0, h, N)

    P0_co2 = (rho_brine*g*h + P0_brine) / exp(Mr_co2 * g * h / R / T_co2)
    P_ncg = P0_co2 * np.exp(Mr_co2 * g * hs_ncg / R / T_co2)

    plt.plot(P_ncg * 1e-5, hs_ncg, label="NCG - {}m".format(h))

    print(P_ncg[0], P_ncg[-1])


plt.show()


