import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib
from math import log


ccplantadjfactor = 1


def Flash_single(T, Pow):
    MaxProducedTemperature = T - 273.15
    ElectricityProduced = Pow

    if ElectricityProduced < 10.:
        C2 = 4.8472E-2
        C1 = -35.2186
        C0 = 8.4474E3
        D2 = 4.0604E-2
        D1 = -29.3817
        D0 = 6.9911E3
        PLL = 5.
        PRL = 10.
    elif ElectricityProduced < 25.:
        C2 = 4.0604E-2
        C1 = -29.3817
        C0 = 6.9911E3
        D2 = 3.2773E-2
        D1 = -23.5519
        D0 = 5.5263E3
        PLL = 10.
        PRL = 25.
    elif ElectricityProduced < 50.:
        C2 = 3.2773E-2
        C1 = -23.5519
        C0 = 5.5263E3
        D2 = 3.4716E-2
        D1 = -23.8139
        D0 = 5.1787E3
        PLL = 25.
        PRL = 50.
    elif ElectricityProduced < 75.:
        C2 = 3.4716E-2
        C1 = -23.8139
        C0 = 5.1787E3
        D2 = 3.5271E-2
        D1 = -24.3962
        D0 = 5.1972E3
        PLL = 50.
        PRL = 75.
    else:
        C2 = 3.5271E-2
        C1 = -24.3962
        C0 = 5.1972E3
        D2 = 3.3908E-2
        D1 = -23.4890
        D0 = 5.0238E3
        PLL = 75.
        PRL = 100.
    maxProdTemp = MaxProducedTemperature
    CCAPPLL = C2 * maxProdTemp ** 2 + C1 * maxProdTemp + C0
    CCAPPRL = D2 * maxProdTemp ** 2 + D1 * maxProdTemp + D0
    b = log(CCAPPRL / CCAPPLL) / log(PRL / PLL)
    a = CCAPPRL / PRL ** b
    # factor 0.75 to make double flash 25% more expansive than single flash
    Cplantcorrelation = (0.8 * a * pow(ElectricityProduced, b) * ElectricityProduced * 1000. / 1E6)

    # 1.02 to convert cost from 2012 to 2016 #factor 1.15 for 15% contingency and 1.12 for 12% indirect costs. factor 1.10 to convert from 2016 to 2022 factor 1.03 to convert from 2022 to 2023
    Cplant = 1.12 * 1.15 * ccplantadjfactor * Cplantcorrelation * 1.02 * 1.10 * 1.03

    return Cplant


with open("../../06_DSC_single_flash/sensitivity_results.json", "r") as file:
    results = json.load(file)

ts = []
qs = []
fluids = []
for result in results:
    if result:
        ts.append(result["Hot fluid input1"])
        qs.append(result["Hot fluid input2"])

ts = list(set(ts))
ts.sort()
qs = list(set(qs))
qs.sort()

SpecCost = [[1e15 + 0 for q in qs] for t in ts]
LCOE = [[1e15 for q in qs] for t in ts]
Cost = [[1e15 for q in qs] for t in ts]
Wnet = [[1e-15 for q in qs] for t in ts]

for result in results:
    if result:
        t_id = ts.index(result["Hot fluid input1"])
        q_id = qs.index(result["Hot fluid input2"])

        SpecCost[t_id][q_id] = result["SpecificCost"]
        LCOE[t_id][q_id] = result["LCOE"]
        Cost[t_id][q_id] = result["Cost"]
        Wnet[t_id][q_id] = -result["NetPow_elec"]*1e-6

qs = [q * 100 for q in qs]

if __name__ == "__main__":
    fig, ax = plt.subplots(ncols=2)

    ts.reverse()
    SpecCost.reverse()
    LCOE.reverse()

    colors = [plt.cm.Greys([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Oranges([1, 0.85, 0.65, 0.45, 0.375, 0.25]),
              plt.cm.Blues([1, 0.85, 0.65, 0.45, 0.375, 0.25])]

    # The specific cost plot
    ax[0].plot([0, 1], [ -1, -1], label="PowerCycle", color=colors[1][2])
    ax[0].plot([0, 1], [ -1, -1], label="GEOPHIRES-X", color=colors[2][2])

    for i, t in enumerate(SpecCost):

        spec_c = []
        for j, q in enumerate(qs):
            spec_c.append(Flash_single(ts[i], Wnet[i][j])*1000/Wnet[i][j])

        label = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(ts[i]) + "}{\\K}"

        # ax[0].plot([0, 1], [ -1, -1], label=label, color=colors[0][i])
        ax[0].plot(qs, t, color=colors[1][i])
        ax[0].plot(qs, spec_c, color=colors[2][i])


    ax[0].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[0].set_ylabel("Specific Cost/\\unit{\\USD_{2023}\\per\\kilo\\watt}")
    ax[0].set_ylim(0, None)
    ax[0].legend()

    for i, t in enumerate(LCOE):
        label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(ts[i]) + "}{\\K}"
        ax[1].plot([0, 1], [ -1, -1], label=label, color=colors[0][i])
        ax[1].plot(qs, t, color=colors[1][i])

    ax[1].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax[1].set_ylabel("LCOE/\\unit{\\USD_{2023}\\per\\MWh}")
    ax[1].set_ylim(0, None)
    ax[1].legend()

    ts.reverse()
    SpecCost.reverse()
    LCOE.reverse()

    tikzplotlib.save("Plots/DSC_SingleFlash_Costs.tex")

# LEGACY
if __name__ == "__main_":
    fig, ax = plt.subplots()
    ts.reverse()
    SpecCost.reverse()
    colors = plt.cm.Oranges([1, 0.85, 0.65, 0.45, 0.375, 0.25])

    for i, t in enumerate(SpecCost):
        label = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(ts[i]) + "}{\\K}"
        ax.plot(qs, t, label=label, color=colors[i])


    ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("Specific Cost/\\unit{\\USD_{2023}\\per\\kilo\\watt}")
    ax.legend()

    ts.reverse()
    SpecCost.reverse()

    tikzplotlib.save("Plots/DSC_SingleFlash_SpecCost.tex")

# LEGACY
if __name__ == "__main_":
    fig, ax = plt.subplots()
    ts.reverse()
    LCOE.reverse()
    colors = plt.cm.Oranges([1, 0.85, 0.65, 0.45, 0.375, 0.25])

    for i, t in enumerate(LCOE):
        label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(ts[i]) + "}{\\K}"
        ax.plot(qs, t, label=label, color=colors[i])

    ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("LCOE/\\unit{\\USD_{2023}\\per\\kilo\\watt\\per\\h}")
    ax.legend()

    ts.reverse()
    LCOE.reverse()

    tikzplotlib.save("Plots/DSC_SingleFlash_LCOE.tex")

# LEGACY
if __name__ == "__main_":
    fig, ax = plt.subplots()
    ts.reverse()
    Cost.reverse()
    colors = plt.cm.Oranges([1, 0.85, 0.65, 0.45, 0.375, 0.25])

    for i, t in enumerate(Cost):
        label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(ts[i]) + "}{\\K}"
        ax.plot(qs, t, label=label, color=colors[i])

    ax.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    ax.set_ylabel("Cost/\\unit{\\mega\\USD_{2023}}")
    ax.legend()

    ts.reverse()
    Cost.reverse()

    # tikzplotlib.save("Plots/DSC_SingleFlash_Costs.tex")

plt.show()
