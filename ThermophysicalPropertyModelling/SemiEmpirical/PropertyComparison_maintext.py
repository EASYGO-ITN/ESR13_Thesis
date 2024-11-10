import matplotlib.pyplot as plt
import numpy as np
import tikzplotlib
import math

from CombinedModel import WaterCO2, Water, CO2
from CombinedModel import Model
nZ = 5
nT = 6
nP = 40

# TODO the interpolation needs more work... it becomes discontinuous at some point.
#  following this, also try the validation with the CoolProp composition

# zCs = np.linspace(0, 1, nZ)
# zCs = [0, 0.054799291699558, 0.115069670221708, 0.211855398583397, 0.344578258389676, 0.655421741610324, 0.788144601416603, 0.884930329778292, 0.945200708300442, 1]

zC = 0.5

ts = np.linspace(298, 300+273.15, nT)
# ps = np.logspace(5, 7, nP)
# ps = np.linspace(1e5, 1e7, nP)
ps = np.logspace(math.log10(1e5), math.log10(599e5), nP)
ps_bar = ps*1e-5

colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]
nColors = len(colors)

fig, axs = plt.subplots(ncols=5)
figb, axsb = plt.subplots(ncols=5)


axs[0].set_ylabel("Density/\\unit{\\mole\\per\\cubic\\m}")
axs[1].set_ylabel("Volume/\\unit{\\cubic\\m\\per\\mole}")
axs[2].set_ylabel("Enthalpy/\\unit{\\joule\\per\\mole}")
axs[3].set_ylabel("Entropy/\\unit{\\joule\\per\\mole\\K}")
axs[4].set_ylabel("Quality/\\unit{\\mole\\per\\mole}")

axs[0].set_xlabel("Pressure/\\unit{\\bar}")
axs[1].set_xlabel("Pressure/\\unit{\\bar}")
axs[2].set_xlabel("Pressure/\\unit{\\bar}")
axs[3].set_xlabel("Pressure/\\unit{\\bar}")
axs[4].set_xlabel("Pressure/\\unit{\\bar}")

axs[0].set_yscale("log")
axs[1].set_yscale("log")

# axs[0].set_xlim([0,100])
# axs[1].set_xlim([0,100])
# axs[2].set_xlim([0,100])
# axs[3].set_xlim([0,100])
# axs[4].set_xlim([0,100])

axs[0].set_ylim([1e1,1e5])
axs[1].set_ylim([1e-5,1e-1])
axs[2].set_ylim([-1e4,3.5e4])
# axs[3].set_ylim([0,100])
axs[4].set_ylim([-0.05,1.05])

axsb[0].set_ylabel("\\(\\frac{\\rho^{HEOS Mix}}{\\rho^{Couples}}\\)")
axsb[1].set_ylabel("\\(\\frac{\\v^{HEOS Mix}}{\\v^{Coupled}}\\)")
axsb[2].set_ylabel("\\(\\frac{\\h^{HEOS Mix}}{\\h^{Coupled}}\\)")
axsb[3].set_ylabel("\\(\\frac{\\s^{HEOS Mix}}{\\s^{Coupled}}\\)")
axsb[4].set_ylabel("\\(\\frac{\\q^{HEOS Mix}}{\\q^{Coupled}}\\)")

axsb[0].set_xlabel("Pressure/\\unit{\\bar}")
axsb[1].set_xlabel("Pressure/\\unit{\\bar}")
axsb[2].set_xlabel("Pressure/\\unit{\\bar}")
axsb[3].set_xlabel("Pressure/\\unit{\\bar}")
axsb[4].set_xlabel("Pressure/\\unit{\\bar}")

axsb[0].set_ylim([0.75,1.25])
axsb[1].set_ylim([0.75,1.25])
axsb[2].set_ylim([0.75,1.25])
axsb[3].set_ylim([0.75,1.25])
axsb[4].set_ylim([0.75,1.25])

# axsb[0].set_xlim([0,100])
# axsb[1].set_xlim([0,100])
# axsb[2].set_xlim([0,100])
# axsb[3].set_xlim([0,100])
# axsb[4].set_xlim([0,100])

# add dummy lines for labels
axs[4].plot([0,0],[1.1,1.1], "k", label="Coupled Model")
axs[4].plot([0,0],[1.1,1.1], "kx", label="HEOS mixture")

axsb[4].plot([0,0],[2.1,2.1], "k", label="Coupled Model")
axsb[4].plot([0,0],[2.1,2.1], "kx", label="HEOS mixture")

# initialise the fluid states
model = Model()
water = Water()
co2 = CO2()
mixture = WaterCO2()

# calculate the new model
for j, t in enumerate(ts):

    label = "\\qty{" + str(int(t)) + "}{" + "\\K}"

    color = colors[j % nColors]

    D = np.empty(nP)
    V = np.empty(nP)
    H = np.empty(nP)
    S = np.empty(nP)
    A = np.empty(nP)

    Dcp = np.empty(nP)
    Vcp = np.empty(nP)
    Hcp = np.empty(nP)
    Scp = np.empty(nP)
    Acp = np.empty(nP)

    for k, p in enumerate(ps):
        D[k], V[k], H[k], S[k], g, vap, liq, A[k] = model.calc(p, t, (1-zC), zC)

        try:
            Dcp[k], Vcp[k], Hcp[k], Scp[k], g, vap, liq, Acp[k] = mixture.calc(p, t, (1-zC), zC)
        except:
            Dcp[k], Vcp[k], Hcp[k], Scp[k], g, vap, liq, Acp[k] = np.NAN, np.NAN, np.NAN, np.NAN, np.NAN, np.NAN, np.NAN, np.NAN

    axs[0].plot(ps_bar, D, label=label, color=color)
    axs[1].plot(ps_bar, V, label=label, color=color)
    axs[2].plot(ps_bar, H, label=label, color=color)
    axs[3].plot(ps_bar, S, label=label, color=color)
    axs[4].plot(ps_bar, A, label=label, color=color)

    axs[0].plot(ps_bar, Dcp, "x", color=color)
    axs[1].plot(ps_bar, Vcp, "x", color=color)
    axs[2].plot(ps_bar, Hcp, "x", color=color)
    axs[3].plot(ps_bar, Scp, "x", color=color)
    axs[4].plot(ps_bar, Acp, "x", color=color)

    Aratio = (A+1e-6)/(Acp+1e-6)
    Aratio[Aratio>10] = np.NAN
    axsb[0].plot(ps_bar, (D+1e-6)/(Dcp+1e-6), label=label, color=color)
    axsb[1].plot(ps_bar, (V+1e-10)/(Vcp+1e-10), label=label, color=color)
    axsb[2].plot(ps_bar, (H+1e-6)/(Hcp+1e-6), label=label, color=color)
    axsb[3].plot(ps_bar, (S+1e-6)/(Scp+1e-6), label=label, color=color)
    axsb[4].plot(ps_bar, Aratio, label=label, color=color)

axs[4].legend()
axsb[4].legend()

plt.tight_layout()
# plt.get_current_fig_manager().window.showMaximized()
plt.show()

# tikzplotlib.save("LatexFiles/Properties_maintext.tex", figure=fig)
# tikzplotlib.save("LatexFiles/Ratios_maintext.tex", figure=figb)
