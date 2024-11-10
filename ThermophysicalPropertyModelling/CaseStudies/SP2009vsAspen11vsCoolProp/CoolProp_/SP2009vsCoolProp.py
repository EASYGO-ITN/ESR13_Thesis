import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib
from SP2009 import SpycherPruss2009
import CoolProp as cp

colors = {250:"#1f77b4", 200:"#ff7f0e", 150:"#2ca02c", 99:"#d62728", 60: "#9467bd",31: "#8c564b", 20: "#e377c2"}

ts = [250, 200, 150, 99, 60, 31, 20]
ps = [1, 2,3,4,5,6, 7,8, 9,10,11, 13, 15, 17, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 54, 57, 60 , 63, 66, 69, 72, 75, 80, 85, 90, 95, 100, 125, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600]

mixture = cp.AbstractState("HEOS", "Water&CarbonDioxide")
mixture.set_mole_fractions([10/11, 1/11])

fig1, ax1 = plt.subplots()
ax1.plot([-1,-1],[1000,1000], "k--", label="CoolProp")
ax1.plot([-1,-1],[1000,1000], "k", label="SP2009")
for t in ts:
    label = "\\qty{" + str(t) + "}{" + "\\degreeCelsius}"
    yH = [SpycherPruss2009().calc_yH2O(p*1e5, t+273.15) for p in ps]
    ax1.plot(ps, yH, color=colors[t], label=label)

    yH_cp = []
    for p in ps:
        try:
            mixture.update(cp.PT_INPUTS, p*1e5, t+273.15)
            yH_cp.append(mixture.mole_fractions_vapor()[0]*100)
        except:
            yH_cp.append(np.NaN)
    ax1.plot(ps, yH_cp, color=colors[t], linestyle="--")

ax1.set_xlabel("Pressure/\\unit{\\bar}")
ax1.set_ylabel("\\(y_{H_2O}\\)/\\unit{\\percent}")
ax1.set_yscale("log")
ax1.set_xlim((0, 600))
ax1.legend()
# plt.show()

tikzplotlib.save("SP2009vsCoolProp_yH2O.tex")


fig2, ax2 = plt.subplots()
ax2.plot([-1,-1],[1000,1000], "k--", label="CoolProp")
ax2.plot([-1,-1],[1000,1000], "k", label="SP2009")
for t in ts:
    if t <= 99:
        label = "\\qty{" + str(t) + "}{" + "\\degreeCelsius}"
        xC = [SpycherPruss2009().calc_xCO2(p*1e5, t+273.15) for p in ps]
        ax2.plot(ps, xC, color=colors[t], label=label)

        xC_cp = []
        for p in ps:
            try:
                mixture.update(cp.PT_INPUTS, p*1e5, t+273.15)
                xC_cp.append(mixture.mole_fractions_liquid()[1]*100)
            except:
                xC_cp.append(np.NaN)
        ax2.plot(ps, xC_cp, color=colors[t], linestyle="--")

ax2.set_xlabel("Pressure/\\unit{\\bar}")
ax2.set_ylabel("\\(x_{CO_2}\\)/\\unit{\\percent}")
ax2.set_xlim((0, 600))
ax2.set_ylim((0, 10))
ax2.legend()
# plt.show()

tikzplotlib.save("SP2009vsCoolProp_xCO2_part1.tex")


fig3, ax3 = plt.subplots()
ax3.plot([-1,-1],[1000,1000], "k--", label="CoolProp")
ax3.plot([-1,-1],[1000,1000], "k", label="SP2009")
for t in ts:
    if t >= 99:
        label = "\\qty{" + str(t) + "}{" + "\\degreeCelsius}"
        xC = [SpycherPruss2009().calc_xCO2(p*1e5, t+273.15) for p in ps]
        ax3.plot(ps, xC, color=colors[t], label=label)

        xC_cp = []
        for p in ps:
            try:
                mixture.update(cp.PT_INPUTS, p*1e5, t+273.15)
                xC_cp.append(mixture.mole_fractions_liquid()[1]*100)
            except:
                xC_cp.append(np.NaN)
        ax3.plot(ps, xC_cp, color=colors[t], linestyle="--")

ax3.set_xlabel("Pressure/\\unit{\\bar}")
ax3.set_ylabel("\\(x_{CO_2}\\)/\\unit{\\percent}")
ax3.set_xlim((0, 600))
ax3.set_ylim((0, 10))
ax3.legend()
# plt.show()

tikzplotlib.save("SP2009vsCoolProp_xCO2_part2.tex")


fig1a, ax1a = plt.subplots()
for t in ts:
    label = "\\qty{" + str(t) + "}{" + "\\degreeCelsius}"

    yH = [SpycherPruss2009().calc_yH2O(p * 1e5, t + 273.15) for p in ps]
    yH_cp = []
    for p in ps:
        try:
            mixture.update(cp.PT_INPUTS, p*1e5, t+273.15)
            yH_cp.append(mixture.mole_fractions_vapor()[0]*100)
            # alpha = (mixture.get_mole_fractions()[1] - mixture.mole_fractions_liquid()[1]) / (mixture.mole_fractions_vapor()[1] - mixture.mole_fractions_liquid()[1])
            # if 0<alpha<1:
            #     yH_cp.append(mixture.mole_fractions_liquid()[1]*100)
            # else:
            #     yH_cp.append(np.NaN)
        except:
            yH_cp.append(np.NaN)
    yH_cp = np.array(yH_cp)
    diff = yH_cp/yH

    ax1a.plot(ps, diff, color=colors[t], label=label)

ax1a.set_xlabel("Pressure/\\unit{\\bar}")
ax1a.set_ylabel("\\(\\frac{y_{H_2O}^{Aspen}}{y_{H_2O}^{SP2009}}\\)")
# ax1a.set_yscale("log")
ax1a.set_xlim((0, 600))
ax1a.legend()

tikzplotlib.save("SP2009vsCoolProp_yH2O_ratio.tex")


fig2a, ax2a = plt.subplots()
for t in ts:
    label = "\\qty{" + str(t) + "}{" + "\\degreeCelsius}"

    yH = [SpycherPruss2009().calc_xCO2(p * 1e5, t + 273.15) for p in ps]
    yH_cp = []
    for p in ps:
        try:
            mixture.update(cp.PT_INPUTS, p*1e5, t+273.15)
            yH_cp.append(mixture.mole_fractions_liquid()[1] * 100)
            # alpha = (mixture.get_mole_fractions()[1] - mixture.mole_fractions_liquid()[1]) / (mixture.mole_fractions_vapor()[1] - mixture.mole_fractions_liquid()[1])
            # if 0<alpha<1:
            #     yH_cp.append(mixture.mole_fractions_liquid()[1]*100)
            # else:
            #     yH_cp.append(np.NaN)
        except:
            yH_cp.append(np.NaN)
    yH_cp = np.array(yH_cp)
    diff = yH_cp/yH

    ax2a.plot(ps, diff, color=colors[t], label=label)

ax2a.set_xlabel("Pressure/\\unit{\\bar}")
ax2a.set_ylabel("\\(\\frac{x_{CO_2}^{Aspen}}{x_{CO_2}^{SP2009}}\\)")
# ax2a.set_yscale("log")
ax2a.set_xlim((0, 600))
ax2a.set_ylim((0, 2))
ax2a.legend()

tikzplotlib.save("SP2009vsCoolProp_xCO2_ratio.tex")

plt.show()