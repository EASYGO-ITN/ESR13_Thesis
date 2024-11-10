import math

import numpy as np
import matplotlib.pyplot as plt

from FluidProperties.fluid import Fluid

zH2O = [1.0, 0.999, 0.99, 0.98, 0.95, 0.9, 0.8, 0.6, 0.4, 0.2, 0.1, 0.05, 0.02, 0.01, 0.001, 0]
# zH2O = [1.0, 0.99, 0.95, 0.6, 0.1]

# zH2O = [0.6]

n_p = 5
ps = np.logspace(math.log10(1e4), math.log10(100*1e5), n_p)

n_t = 25
ts = np.linspace(290, 500, n_t)

for i, zH in enumerate(zH2O):
    brine = Fluid(["water", zH, "carbondioxide", 1 - zH], engine="geoprop")

    fig, axs = plt.subplots(3, 2)

    for j, p in enumerate(ps):
        res_h = np.zeros(n_t)
        res_s = np.zeros(n_t)
        res_q = np.zeros(n_t)
        res_d = np.zeros(n_t)
        res_z = np.zeros(n_t)

        for k, t in enumerate(ts):

            try:
                brine.update("PT", p, t)

                res_h[k] = brine.properties.H
                res_s[k] = brine.properties.S
                res_q[k] = brine.properties.Q
                res_d[k] = brine.properties.D
                res_z[k] = brine.composition[0] - zH

            except:
                res_h[k] = np.NaN
                res_s[k] = np.NaN
                res_q[k] = np.NaN
                res_d[k] = np.NaN
                res_z[k] = np.NaN

        axs[0, 0].plot(ts, res_h, marker="o", linestyle=":", label="{:.1e} Pa".format(p))
        axs[0, 0].legend(loc="upper left", fontsize="8")
        axs[0, 0].set_xlabel("Temperature, K")
        axs[0, 0].set_ylabel("Enthalpy, J/kg")

        axs[0, 1].plot(ts, res_s, marker="o", linestyle=":")
        axs[0, 1].set_xlabel("Temperature, K")
        axs[0, 1].set_ylabel("Entropy, J/kg/K")

        axs[1, 0].plot(ts, res_q, marker="o", linestyle=":")
        axs[1, 0].set_xlabel("Temperature, K")
        axs[1, 0].set_ylabel("Quality, -")
        axs[1, 0].set_ylim((0, 1))

        axs[1, 1].plot(ts, res_d, marker="o", linestyle=":")
        axs[1, 1].set_xlabel("Temperature, K")
        axs[1, 1].set_ylabel("Density, kg/m3")
        # axs[1, 1].legend(loc="upper left")

        axs[2, 0].plot(ts, res_z, marker="o", linestyle=":")
        axs[2, 0].set_xlabel("Temperature, K")
        axs[2, 0].set_ylabel("Delta ZH, kg/m3")

    fig.suptitle("zH2O={}".format(zH))
    # fig.legend(bbox_to_anchor=(1.1, 0.5), borderaxespad=1)
    # fig.show()

    mng = plt.get_current_fig_manager()
    mng.full_screen_toggle()
    fig.savefig("zH2O={}.svg".format(zH))

    print("Tadaaa: {} done".format(zH))
