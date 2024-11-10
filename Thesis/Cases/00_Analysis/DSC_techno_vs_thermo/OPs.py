import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib
from CoolProp.CoolProp import PropsSI

def get_techno():
    with open("../../10_DSC_single_flash_techno_SpecCost/sensitivity_results.json", "r") as file:
        results = json.load(file)

    ts = []
    qs = []
    for result in results:
        if result:
            ts.append(result["Hot fluid input1"])
            qs.append(result["Hot fluid input2"])

    ts = list(set(ts))
    ts.sort()
    qs = list(set(qs))
    qs.sort()

    Xflash = [[np.NAN + 0 for q in qs] for t in ts]
    Pmin = [[np.NAN + 0 for q in qs] for t in ts]
    DT_pinch_cond = [[np.NAN + 0 for q in qs] for t in ts]

    for result in results:
        if result:

            t_id = ts.index(result["Hot fluid input1"])
            q_id = qs.index(result["Hot fluid input2"])

            Xflash[t_id][q_id] = 100*(1 - result["Pflash"] / result["Pin"])
            Pmin[t_id][q_id] = result["Pmin"]*1e-5
            DT_pinch_cond[t_id][q_id] = result["Var 2"]

    qs = [q * 100 for q in qs]

    return Xflash, Pmin, DT_pinch_cond, ts, qs


def get_thermo():
    with open("../../06_DSC_single_flash/sensitivity_results.json", "r") as file:
        results = json.load(file)

    ts = []
    qs = []
    for result in results:
        if result:
            ts.append(result["Hot fluid input1"])
            qs.append(result["Hot fluid input2"])

    ts = list(set(ts))
    ts.sort()
    qs = list(set(qs))
    qs.sort()

    Xflash = [[np.NAN + 0 for q in qs] for t in ts]
    Pmin = [[np.NAN + 0 for q in qs] for t in ts]
    DT_pinch_cond = [[np.NAN + 0 for q in qs] for t in ts]

    for result in results:
        if result:
            t_id = ts.index(result["Hot fluid input1"])
            q_id = qs.index(result["Hot fluid input2"])

            Xflash[t_id][q_id] = 100*(1 - result["Pflash"] / result["Pin"])
            Pmin[t_id][q_id] = result["Pmin"] * 1e-5
            DT_pinch_cond[t_id][q_id] = 5

    qs = [q * 100 for q in qs]

    return Xflash, Pmin, DT_pinch_cond, ts, qs

techno_Xflash, techno_Pmin, techno_DT_pinch_cond, techno_ts, techno_qs = get_techno()
thermo_Xflash, thermo_Pmin, thermo_DT_pinch_cond, thermo_ts, thermo_qs = get_thermo()

nT = len(techno_ts)
colors = [plt.cm.Oranges(np.linspace(0.3, 1, nT)),
          plt.cm.Blues(np.linspace(0.3, 1, nT)),
          plt.cm.Greys(np.linspace(0.3, 1, nT)),
          ]

# Xflash
if __name__ == "__main__":
    fig, axs = plt.subplots(2)
    for i in range(nT):
        label = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(techno_ts[i])+"}{\\K}"
        axs[0].plot([0,1], [-1,-1], label=label, color=colors[2][i])
        axs[0].plot(techno_qs, techno_Xflash[i], color=colors[0][i])
        axs[1].plot(thermo_qs, thermo_Xflash[i], color=colors[1][i])

    axs[0].set_title("Techno-Economic Opt.")
    axs[0].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    axs[0].set_ylabel("\\(1-\\frac{P_{flash}}{P_{geo}^{in}}\\)/\\unit{\\percent}")
    axs[0].set_ylim(0, 100)
    axs[0].legend()

    axs[1].set_title("Thermodynamic Opt.")
    axs[1].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    axs[1].set_ylabel("\\(1-\\frac{P_{flash}}{P_{geo}^{in}}\\)/\\unit{\\percent}")
    axs[1].set_ylim(0, 100)

    tikzplotlib.save("Plots/Xflash.tex")

# DT pinch cond
if __name__ == "__main__":
    fig, axs = plt.subplots()

    axs.plot([0, 1], [-1, -1], label="Techno-economic Opt.", color=colors[0][3])
    axs.plot([0, 1], [-1, -1], label="Thermodynamic Opt.", color=colors[1][3])
    for i in range(nT):
        label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(techno_ts[i]) + "}{\\K}"
        axs.plot([0, 1], [-1, -1], label=label, color=colors[2][i])
        axs.plot(techno_qs, techno_DT_pinch_cond[i], color=colors[0][i])
        axs.plot(thermo_qs, thermo_DT_pinch_cond[i], color=colors[1][i])

    # axs.set_title("Techno-Economic Opt.")
    axs.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    axs.set_ylabel("\\(\\Delta T_{cond}^{min}\\)/\\unit{\\K}")
    axs.set_ylim(0, 35)
    axs.legend()

    tikzplotlib.save("Plots/DTpinchCond.tex")

# Pcond
if __name__ == "__main__":
    fig, axs = plt.subplots()
    axs.plot([0, 1], [0.01, 0.01], label="Techno-economic Opt.", color=colors[0][3])
    axs.plot([0, 1], [0.01, 0.01], label="Thermodynamic Opt.", color=colors[1][3])
    for i in range(nT):
        label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(techno_ts[i]) + "}{\\K}"
        axs.plot([0, 1], [0.01, 0.01], label=label, color=colors[2][i])
        axs.plot(techno_qs, techno_Pmin[i], color=colors[0][i])
        axs.plot(thermo_qs, thermo_Pmin[i], color=colors[1][i])

    # axs.set_title("Techno-Economic Opt.")
    axs.set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    axs.set_ylabel("Condensation Pressure/\\unit{\\bar}")
    axs.set_ylim(0.08, 1)
    axs.set_yscale("log")
    axs.legend()

    tikzplotlib.save("Plots/Pmin.tex")


plt.show()
