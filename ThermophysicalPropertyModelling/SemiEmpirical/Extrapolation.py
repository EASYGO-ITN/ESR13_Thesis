import CoolProp as cp
from CoolProp.CoolProp import PropsSI
import math
from scipy.optimize import root_scalar

import matplotlib.pyplot as plt
import numpy as np
import tikzplotlib

N_p = 3
ps = np.logspace(5, 7, N_p)

water = cp.AbstractState("?", "water")

# plotting the various methods
fig, axs = plt.subplots(nrows=2, ncols=2)
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]

T_min = 298
N_ex = 50
N_t = 20

# axs[0][0].plot([0], [0], "k", label="WP EOS")
# axs[0][0].plot([0], [0], "ko", label="Saturation")
# axs[0][0].plot([0], [0], "k--", label="G Extrap.")
# axs[0][0].plot([0], [0], "k", linestyle="dotted", label="H\&S Extrap.")
# axs[0][0].plot([0], [0], "k", linestyle="dashdot", label="Rho Extrap.")

# axs[0][1].plot([0], [0], "k", label="WP EOS")
# axs[0][1].plot([0], [0], "ko", label="Saturation")
# axs[0][1].plot([0], [0], "k--", label="G Extrap.")
# axs[0][1].plot([0], [0], "k", linestyle="dotted", label="H\&S Extrap.")
# axs[0][1].plot([0], [0], "k", linestyle="dashdot", label="Rho Extrap.")

axs[1][0].plot([0], [0], "k", label="WP EOS")
axs[1][0].plot([0], [0], "ko", label="Saturation")
axs[1][0].plot([0], [0], "k--", label="G Extrap.")
axs[1][0].plot([0], [0], "k", linestyle="dotted", label="H\&S Extrap.")
axs[1][0].plot([0], [0], "k", linestyle="dashdot", label="Rho Extrap.")

axs[1][1].plot([0], [1], "k", label="WP EOS")
axs[1][1].plot([0], [1], "ko", label="Saturation")
axs[1][1].plot([0], [1], "k--", label="G Extrap.")
axs[1][1].plot([0], [1], "k", linestyle="dotted", label="IdealGas Extrap.")
axs[1][1].plot([0], [1], "k", linestyle="dashdot", label="Power Extrap.")

# Gibbs Energy Extrapolation Functions
if __name__ == "__main__":
    def G_gext(T):
        g = Gsat - (Tsat - T) * dGdT
        return g


    def H_gext(T):
        delta = 1e-6

        a = 1 / T
        g = a * G_gext(1 / a)

        a_ = a * (1 + delta)
        g_ = a_ * G_gext(1 / a_)

        h = (g_ - g) / (a_ - a)
        return h


    def S_gext(T):
        delta = 1e-6
        g = G_gext(T)
        T_ = (1 + delta) * T
        g_ = G_gext(T_)

        s = - (g_ - g) / (T_ - T)
        return s


    def V_gext(T):
        v = Vsat + (Tsat - T) * dSdP  # + Ssat*dTdP
        return v

# Enthalpy and Entropy Extrapolation Functions
if __name__ == "__main__":
    def H_hsext(T):
        h = Hsat - (Tsat - T) * dHdT
        return h

    def S_hsext(T):
        s = Ssat - (Tsat - T) * dSdT
        return s

    def G_hsext(T):
        g = H_hsext(T) - T * S_hsext(T)
        return g

# Vapour-Liquid Density Extrapolation Functions
if __name__ == "__main__":
    def H_density(T):
        v = V_density(T)
        water.update(cp.DmolarT_INPUTS, 1 / v, T)

        h = water.hmolar()
        return h

    def S_density(T):
        v = V_density(T)
        water.update(cp.DmolarT_INPUTS, 1 / v, T)

        s = water.smolar()
        return s

    def G_density(T):
        v = V_density(T)
        water.update(cp.DmolarT_INPUTS, 1 / v, T)

        g = water.gibbsmolar()
        g = H_density(T) - T * S_density(T)
        return g

    def V_density(T):
        v = Vsat * (T / Tsat)
        return v

# Volume Extrapolation Functions
if __name__ == "__main__":
    def V_ideal_ext(T):
        v = Vsat * (T / Tsat)
        return v

    def V_power_ext(T):
        a =  dVdT * Tsat / Vsat
        v = Vsat * (t / Tsat) ** a
        return v


for i, p in enumerate(ps):

    color = colors[i % N_p]

    water.update(cp.PQ_INPUTS, p, 1)
    Tsat = water.T()
    Gsat = water.gibbsmolar()
    Hsat = water.hmolar()
    Ssat = water.smolar()
    Vsat = 1 / water.rhomolar()

    dGdT = water.first_partial_deriv(cp.iGmolar, cp.iT, cp.iP)
    dGdP = water.first_partial_deriv(cp.iGmolar, cp.iP, cp.iT)
    dHdT = water.first_partial_deriv(cp.iHmolar, cp.iT, cp.iP)
    dHdTdT = water.second_partial_deriv(cp.iHmolar, cp.iT, cp.iP, cp.iT, cp.iP)
    dHdP = water.first_partial_deriv(cp.iHmolar, cp.iP, cp.iT)
    dHdTdP = water.second_partial_deriv(cp.iHmolar, cp.iT, cp.iP, cp.iP, cp.iT)
    dSdTdP = water.second_partial_deriv(cp.iSmolar, cp.iT, cp.iP, cp.iP, cp.iT)
    dSdT = water.first_partial_deriv(cp.iSmolar, cp.iT, cp.iP)
    dSdTdT = water.second_partial_deriv(cp.iSmolar, cp.iT, cp.iP, cp.iT, cp.iP)
    dSdP = water.first_partial_deriv(cp.iSmolar, cp.iP, cp.iT)
    dVdT = -Vsat*Vsat*water.first_partial_deriv(cp.iDmolar, cp.iT, cp.iP)

    # calculate the real vapour properties
    tgs = np.linspace(Tsat + 1, Tsat*1.25, N_t)
    ggs = np.empty(N_t)
    hgs = np.empty(N_t)
    sgs = np.empty(N_t)
    vgs = np.empty(N_t)

    for j, t in enumerate(tgs):
        water.update(cp.PT_INPUTS, p, t)
        ggs[j] = water.gibbsmolar()
        hgs[j] = water.hmolar()
        sgs[j] = water.smolar()
        vgs[j] = 1 / water.rhomolar()

    tls = np.linspace(Tsat*0.75, Tsat-1, N_t)
    gls = np.empty(N_t)
    hls = np.empty(N_t)
    sls = np.empty(N_t)
    vls = np.empty(N_t)

    for j, t in enumerate(tls):
        water.update(cp.PT_INPUTS, p, t)
        gls[j] = water.gibbsmolar()
        hls[j] = water.hmolar()
        sls[j] = water.smolar()
        vls[j] = 1 / water.rhomolar()

    # axs[0][0].plot(tgs, ggs, label="P={:.0f} bar".format(p*1e-5), color=color)
    axs[0][0].plot(tgs, ggs, color=color)
    axs[0][0].plot(Tsat, Gsat, "o", color=color)
    axs[0][0].plot(tls, gls, color=color)

    # axs[1][0].plot(tgs, hgs, label="P={:.0f} bar".format(p*1e-5), color=color)
    axs[1][0].plot(tgs, hgs, label="P={:.0f} bar".format(p*1e-5), color=color)
    axs[1][0].plot(Tsat, Hsat, "o", color=color)
    axs[1][0].plot(tls, hls, color=color)

    # axs[0][1].plot(tgs, sgs, label="P={:.0f} bar".format(p*1e-5), color=color)
    axs[0][1].plot(tgs, sgs, color=color)
    axs[0][1].plot(Tsat, Ssat, "o", color=color)
    axs[0][1].plot(tls, sls, color=color)

    axs[1][1].plot(tgs, vgs, label="P={:.0f} bar".format(p*1e-5), color=color)
    axs[1][1].plot(Tsat, Vsat, "o", color=color)
    axs[1][1].plot(tls, vls, color=color)

    ts = np.append(tls, tgs)

    # Gibbs Energy Extrapolation
    gs_gext = np.empty(N_t*2)
    hs_gext = np.empty(N_t*2)
    ss_gext = np.empty(N_t*2)
    vs_gext = np.empty(N_t*2)

    for j, t in enumerate(ts):
        gs_gext[j] = G_gext(t)
        hs_gext[j] = H_gext(t)
        ss_gext[j] = S_gext(t)
        vs_gext[j] = V_gext(t)

    axs[0][0].plot(ts, gs_gext, "--", color=color)
    axs[1][0].plot(ts, hs_gext, "--", color=color)
    axs[0][1].plot(ts, ss_gext, "--", color=color)
    axs[1][1].plot(ts, vs_gext, "--", color=color)

    # Enthalpy and Entropy Extrapolation
    gs_hsext = np.empty(N_t*2)
    hs_hsext = np.empty(N_t*2)
    ss_hsext = np.empty(N_t*2)

    for j, t in enumerate(ts):
        gs_hsext[j] = G_hsext(t)
        hs_hsext[j] = H_hsext(t)
        ss_hsext[j] = S_hsext(t)

    axs[0][0].plot(ts, gs_hsext, linestyle="dotted", color=color)
    axs[1][0].plot(ts, hs_hsext, linestyle="dotted", color=color)
    axs[0][1].plot(ts, ss_hsext, linestyle="dotted", color=color)

    # Density Extrapolation
    gs_density = np.empty(N_t*2)
    hs_density = np.empty(N_t*2)
    ss_density = np.empty(N_t*2)

    for j, t in enumerate(ts):
        gs_density[j] = G_density(t)
        hs_density[j] = H_density(t)
        ss_density[j] = S_density(t)

    axs[0][0].plot(ts, gs_density, linestyle="dashdot", color=color)
    axs[1][0].plot(ts, hs_density, linestyle="dashdot", color=color)
    axs[0][1].plot(ts, ss_density, linestyle="dashdot", color=color)

    # VOlume Extrapolation
    vs_ideal = np.empty(N_t*2)
    vs_power = np.empty(N_t*2)

    for j, t in enumerate(ts):
        vs_ideal[j] = V_ideal_ext(t)
        vs_power[j] = V_power_ext(t)

    axs[1][1].plot(ts, vs_ideal, linestyle="dotted", color=color)
    axs[1][1].plot(ts, vs_power, linestyle="dashdot", color=color)



axs[0][0].set_xlabel("Temperature/\\unit{\\K}")
axs[0][0].set_ylabel("Gibbs Energy/\\unit{\\joule\\per\\mole}")
axs[0][0].set_ylim([-20000, 10000])
axs[0][0].set_xlim([298, 700])
# axs[0][0].legend()

axs[1][0].set_xlabel("Temperature/\\unit{\\K}")
axs[1][0].set_ylabel("Enthalpy/\\unit{\\joule\\per\\mole}")
axs[1][0].set_ylim([0, 60000])
axs[1][0].set_xlim([298, 700])
axs[1][0].legend()

axs[0][1].set_xlabel("Temperature/\\unit{\\K}")
axs[0][1].set_ylabel("Entropy,\\unit{\\joule\\per\\mole\\K}")
axs[0][1].set_ylim([0, 150])
axs[0][1].set_xlim([298, 700])
# axs[0][1].legend()

axs[1][1].set_xlabel("Temperature/\\unit{\\K}")
axs[1][1].set_ylabel("Volume/\\unit{\\cubic\\m \\per\\mole}")
axs[1][1].set_yscale("log")
axs[1][1].set_xlim([298, 700])
axs[1][1].set_ylim([1e-5, 1e-1])
axs[1][1].legend()

fig.tight_layout()
# plt.get_current_fig_manager().window.showMaximized()
plt.show()

# tikzplotlib.save("ExtrapolationFuncs.tex")
