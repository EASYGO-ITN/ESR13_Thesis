import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib
from CoolProp.CoolProp import PropsSI
import math


def get_techno_results():
    with open("../../08_SimpleORC_techno_specCost/Part_a/sensitivity_results.json", "r") as file:
        results_a = json.load(file)
    with open("../../08_SimpleORC_techno_specCost/Part_b/sensitivity_results.json", "r") as file:
        results_b = json.load(file)
    with open("../../08_SimpleORC_techno_specCost/Part_c/sensitivity_results.json", "r") as file:
        results_c = json.load(file)

    results = results_a + results_b + results_c

    ts = []
    qs = []
    fluids = []
    for result in results:
        if result:
            ts.append(result["Hot fluid input1"])
            qs.append(result["Hot fluid input2"])

            if result["Working fluid comp"] not in fluids:
                fluids.append(result["Working fluid comp"])

    ts = list(set(ts))
    ts.sort()
    qs = list(set(qs))
    qs.sort()
    # fluids.sort()

    fluids = [["n-Propane", 1],
              # ["CycloPropane", 1],
              ["IsoButane", 1],
              ["n-Butane", 1],
              ["Isopentane", 1],
              # ["Isohexane", 1],
              ["Cyclopentane", 1],
              ["n-Heptane", 1]]

    Pmax = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    Tmax = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    Tmin = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    DTsh = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]

    PreH_pinch = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    Evap_pinch = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    SupH_pinch = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    Cond_pinch = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]

    for result in results:
        if result:

            t_id = ts.index(result["Hot fluid input1"])
            q_id = qs.index(result["Hot fluid input2"])
            f_id = fluids.index(result["Working fluid comp"])

            Pcrit = PropsSI("Pcrit", fluids[f_id][0])
            Tsat = PropsSI("T", "P", result["Pmax"], "Q", 0, fluids[f_id][0])

            Pmax[f_id][t_id][q_id] = result["Pmax"] / Pcrit
            Tmax[f_id][t_id][q_id] = result["Tmax"]
            Tmin[f_id][t_id][q_id] = result["Tmin"]
            DTsh[f_id][t_id][q_id] = result["Tmax"] - Tsat

            PreH_pinch[f_id][t_id][q_id] = result["Var 3"]
            Evap_pinch[f_id][t_id][q_id] = result["Var 4"]
            SupH_pinch[f_id][t_id][q_id] = result["Var 5"]
            Cond_pinch[f_id][t_id][q_id] = result["Var 6"]


    qs = [q * 100 for q in qs]

    return Pmax, Tmax, Tmin, DTsh, PreH_pinch, Evap_pinch, SupH_pinch, Cond_pinch, ts, qs, fluids

def get_thermo_results():
    with open("../../00_SimpleORC/sensitivity_results.json", "r") as file:
        results_a = json.load(file)
    with open("../../00_SimpleORC_additional_fluids/sensitivity_results.json", "r") as file:
        results_b = json.load(file)

    results = results_a + results_b

    ts = []
    qs = []
    fluids = []
    for result in results:
        if result:
            ts.append(result["Hot fluid input1"])
            qs.append(result["Hot fluid input2"])

            if result["Working fluid comp"] not in fluids:
                fluids.append(result["Working fluid comp"])

    ts = list(set(ts))
    ts.sort()
    qs = list(set(qs))
    qs.sort()
    # fluids.sort()

    fluids = [["n-Propane", 1],
              # ["CycloPropane", 1],
              ["IsoButane", 1],
              ["n-Butane", 1],
              ["Isopentane", 1],
              # ["Isohexane", 1],
              ["Cyclopentane", 1],
              ["n-Heptane", 1]]

    Pmax = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    Tmax = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    Tmin = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
    DTsh = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]

    PreH_pinch = [5, 5]
    Evap_pinch = [10, 10]
    SupH_pinch = [10, 10]
    Cond_pinch = [5, 5]

    for result in results:
        if result:

            t_id = ts.index(result["Hot fluid input1"])
            q_id = qs.index(result["Hot fluid input2"])
            try:
                f_id = fluids.index(result["Working fluid comp"])
            except:
                continue

            Pcrit = PropsSI("Pcrit", fluids[f_id][0])
            Tsat = PropsSI("T", "P", result["Pmax"], "Q", 0, fluids[f_id][0])

            Pmax[f_id][t_id][q_id] = result["Pmax"] / Pcrit
            Tmax[f_id][t_id][q_id] = result["Tmax"]
            Tmin[f_id][t_id][q_id] = result["Tmin"]
            DTsh[f_id][t_id][q_id] = result["Tmax"] - Tsat

    qs = [q * 100 for q in qs]

    return Pmax, Tmax, Tmin, DTsh, PreH_pinch, Evap_pinch, SupH_pinch, Cond_pinch, ts, qs, fluids


Pmax_techno, Tmax_techno, Tmin_techno, DTsh_techno, PreH_pinch_techno, Evap_pinch_techno, SupH_pinch_techno, Cond_pinch_techno, ts_techno, qs_techno, fluids_techno = get_techno_results()
Pmax_thermo, Tmax_thermo, Tmin_thermo, DTsh_thermo, PreH_pinch_thermo, Evap_pinch_thermo, SupH_pinch_thermo, Cond_pinch_thermo, ts_thermo, qs_thermo, fluids_thermo = get_thermo_results()


colors = [plt.cm.Blues(np.linspace(0.3, 1, len(ts_techno))),
          plt.cm.Oranges(np.linspace(0.3, 1, len(ts_techno))),
          plt.cm.Greens(np.linspace(0.3, 1, len(ts_techno))),
          plt.cm.Reds(np.linspace(0.3, 1, len(ts_techno))),
          plt.cm.Purples(np.linspace(0.3, 1, len(ts_techno))),
          plt.cm.Greys(np.linspace(0.3, 1, len(ts_techno)))]


# plot the maximum pressure
fig, axs = plt.subplots(nrows=len(fluids_techno))
axs[-1].plot([0, 1], [-1, -1], "k", label="Techno-economic opt.")

for i, t in enumerate(ts_techno):

    if i == math.floor(len(ts_techno)/2):
        axs[-1].plot([0, 1], [-1, -1], "k--", label="Thermodynamic opt.")

    label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(t) + "}{\\K}"
    axs[-1].plot([0, 1], [-1, -1], label=label, color=colors[-1][i])

for j, fluid in enumerate(fluids_techno):
    axs[j].set_title("{}".format(fluid[0]))

    f_id = fluids_techno.index(fluid)
    for i, p in enumerate(Pmax_techno[f_id]):
        axs[j].plot(qs_techno, p, color=colors[f_id][i])

    f_id = fluids_thermo.index(fluid)
    for i, p in enumerate(Pmax_thermo[f_id]):
        axs[j].plot(qs_thermo, p, "--", color=colors[f_id][i])

    axs[j].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    axs[j].set_ylabel("Reduced Pressure")
    axs[j].set_ylim(0.25, 0.85)

axs[-1].legend()

tikzplotlib.save("Plots/SimpleORC_Pmax.tex", figure=fig)


# plot the maximum temperature
fig, axs = plt.subplots(nrows=len(fluids_techno))
axs[-1].plot([0, 1], [-1, -1], "k", label="Techno-economic opt.")

for i, t in enumerate(ts_techno):

    if i == math.floor(len(ts_techno)/2):
        axs[-1].plot([0, 1], [-1, -1], "k--", label="Thermodynamic opt.")

    label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(t) + "}{\\K}"
    axs[-1].plot([0, 1], [-1, -1], label=label, color=colors[-1][i])

for j, fluid in enumerate(fluids_techno):
    axs[j].set_title("{}".format(fluid[0]))

    f_id = fluids_techno.index(fluid)
    for i, p in enumerate(Tmax_techno[f_id]):
        axs[j].plot(qs_techno, p, color=colors[f_id][i])

    f_id = fluids_thermo.index(fluid)
    for i, p in enumerate(Tmax_thermo[f_id]):
        axs[j].plot(qs_thermo, p, "--", color=colors[f_id][i])

    axs[j].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    axs[j].set_ylabel("\\(T_{max}\\)\\unit{\\K}")
    # axs[j].set_ylim(0.25, 0.85)

axs[-1].legend()

tikzplotlib.save("Plots/SimpleORC_Tmax.tex", figure=fig)


# plot the maximum pressure
fig, axs = plt.subplots(nrows=len(fluids_techno))
axs[-1].plot([0, 1], [-1, -1], "k", label="Techno-economic opt.")

for i, t in enumerate(ts_techno):

    if i == math.floor(len(ts_techno)/2):
        axs[-1].plot([0, 1], [-1, -1], "k--", label="Thermodynamic opt.")

    label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(t) + "}{\\K}"
    axs[-1].plot([0, 1], [-1, -1], label=label, color=colors[-1][i])

for j, fluid in enumerate(fluids_techno):
    axs[j].set_title("{}".format(fluid[0]))

    f_id = fluids_techno.index(fluid)
    for i, p in enumerate(DTsh_techno[f_id]):
        axs[j].plot(qs_techno, p, color=colors[f_id][i])

    f_id = fluids_thermo.index(fluid)
    for i, p in enumerate(DTsh_thermo[f_id]):
        axs[j].plot(qs_thermo, p, "--", color=colors[f_id][i])

    axs[j].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    axs[j].set_ylabel("Superheating/\\unit{\\K}")
    axs[j].set_ylim(0, 20)

axs[-1].legend()

tikzplotlib.save("Plots/SimpleORC_DTsh.tex", figure=fig)


fig, axs = plt.subplots(nrows=len(fluids_techno))
axs[-1].plot([0, 1], [-1, -1], "k", label="Techno-economic opt.")

for i, t in enumerate(ts_techno):

    if i == math.floor(len(ts_techno)/2):
        axs[-1].plot([0, 1], [-1, -1], "k--", label="Thermodynamic opt.")

    label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(t) + "}{\\K}"
    axs[-1].plot([0, 1], [-1, -1], label=label, color=colors[-1][i])

for j, fluid in enumerate(fluids_techno):
    axs[j].set_title("{}".format(fluid[0]))

    f_id = fluids_techno.index(fluid)
    for i, p in enumerate(Tmin_techno[f_id]):
        axs[j].plot(qs_techno, p, color=colors[f_id][i])

    f_id = fluids_thermo.index(fluid)
    for i, p in enumerate(Tmin_thermo[f_id]):
        axs[j].plot(qs_thermo, p, "--", color=colors[f_id][i])

    axs[j].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    axs[j].set_ylabel("\\(T_{min}\\)/\\unit{\\K}")
    axs[j].set_ylim(303, 400)

axs[-1].legend()

tikzplotlib.save("Plots/SimpleORC_Tmin.tex", figure=fig)


fig, axs = plt.subplots(nrows=len(fluids_techno))
axs[-1].plot([0, 1], [-1, -1], "k", label="Techno-economic opt.")

for i, t in enumerate(ts_techno):

    if i == math.floor(len(ts_techno)/2):
        axs[-1].plot([0, 1], [-1, -1], "k--", label="Thermodynamic opt.")

    label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(t) + "}{\\K}"
    axs[-1].plot([0, 1], [-1, -1], label=label, color=colors[-1][i])

for j, fluid in enumerate(fluids_techno):
    axs[j].set_title("{}".format(fluid[0]))

    f_id = fluids_techno.index(fluid)
    for i, p in enumerate(PreH_pinch_techno[f_id]):
        axs[j].plot(qs_techno, p, color=colors[f_id][i])

    f_id = fluids_thermo.index(fluid)
    for i, p in enumerate(PreH_pinch_techno[f_id]):
        axs[j].plot([0, 100], PreH_pinch_thermo, "--", color=colors[f_id][i])

    axs[j].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    axs[j].set_ylabel("\\(\\Delta T_{preh}^{min}\\)/\\unit{\\K}")
    axs[j].set_ylim(0, 35)

axs[-1].legend()

tikzplotlib.save("Plots/SimpleORC_PreH_pinch.tex", figure=fig)


fig, axs = plt.subplots(nrows=len(fluids_techno))
axs[-1].plot([0, 1], [-1, -1], "k", label="Techno-economic opt.")

for i, t in enumerate(ts_techno):

    if i == math.floor(len(ts_techno)/2):
        axs[-1].plot([0, 1], [-1, -1], "k--", label="Thermodynamic opt.")

    label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(t) + "}{\\K}"
    axs[-1].plot([0, 1], [-1, -1], label=label, color=colors[-1][i])

for j, fluid in enumerate(fluids_techno):
    axs[j].set_title("{}".format(fluid[0]))

    f_id = fluids_techno.index(fluid)
    for i, p in enumerate(Evap_pinch_techno[f_id]):
        axs[j].plot(qs_techno, p, color=colors[f_id][i])

    f_id = fluids_thermo.index(fluid)
    for i, p in enumerate(Evap_pinch_techno[f_id]):
        axs[j].plot([0, 100], Evap_pinch_thermo, "--", color=colors[f_id][i])

    axs[j].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    axs[j].set_ylabel("\\(\\Delta T_{evap}^{min}\\)/\\unit{\\K}")
    axs[j].set_ylim(0, 35)

axs[-1].legend()

tikzplotlib.save("Plots/SimpleORC_Evap_pinch.tex", figure=fig)


fig, axs = plt.subplots(nrows=len(fluids_techno))
axs[-1].plot([0, 1], [-1, -1], "k", label="Techno-economic opt.")

for i, t in enumerate(ts_techno):

    if i == math.floor(len(ts_techno)/2):
        axs[-1].plot([0, 1], [-1, -1], "k--", label="Thermodynamic opt.")

    label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(t) + "}{\\K}"
    axs[-1].plot([0, 1], [-1, -1], label=label, color=colors[-1][i])

for j, fluid in enumerate(fluids_techno):
    axs[j].set_title("{}".format(fluid[0]))

    f_id = fluids_techno.index(fluid)
    for i, p in enumerate(SupH_pinch_techno[f_id]):
        axs[j].plot(qs_techno, p, color=colors[f_id][i])

    f_id = fluids_thermo.index(fluid)
    for i, p in enumerate(SupH_pinch_techno[f_id]):
        axs[j].plot([0, 100], SupH_pinch_thermo, "--", color=colors[f_id][i])

    axs[j].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    axs[j].set_ylabel("\\(\\Delta T_{suph}^{min}\\)/\\unit{\\K}")
    axs[j].set_ylim(0, 35)

axs[-1].legend()

tikzplotlib.save("Plots/SimpleORC_SupH_pinch.tex", figure=fig)


fig, axs = plt.subplots(nrows=len(fluids_techno))
axs[-1].plot([0, 1], [-1, -1], "k", label="Techno-economic opt.")

for i, t in enumerate(ts_techno):
    if i == math.floor(len(ts_techno)/2):
        axs[-1].plot([0, 1], [-1, -1], "k--", label="Thermodynamic opt.")

    label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(t) + "}{\\K}"
    axs[-1].plot([0, 1], [-1, -1], label=label, color=colors[-1][i])

for j, fluid in enumerate(fluids_techno):
    axs[j].set_title("{}".format(fluid[0]))

    f_id = fluids_techno.index(fluid)
    for i, p in enumerate(Cond_pinch_techno[f_id]):
        axs[j].plot(qs_techno, p, color=colors[f_id][i])

    f_id = fluids_thermo.index(fluid)
    for i, p in enumerate(Cond_pinch_techno[f_id]):
        axs[j].plot([0, 100], Cond_pinch_thermo, "--", color=colors[f_id][i])

    axs[j].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    axs[j].set_ylabel("\\(\\Delta T_{cond}^{min}\\)/\\unit{\\K}")
    axs[j].set_ylim(0, 35)

axs[-1].legend()

tikzplotlib.save("Plots/SimpleORC_Cond_pinch.tex", figure=fig)


fig, axs = plt.subplots(len(fluids_techno))
for j, fluid in enumerate(fluids_techno):
    axs[j].set_title("{}".format(fluid[0]))

    axs[j].plot([0, 1], [273, 273], "k", label="\\(T_{max}\\)")
    axs[j].plot([0, 1], [273, 273], "k--", label="\\(T_{min}\\)")
    # axs[j].plot([0, 1], [273, 273], "--", label="\\(T_{geo}^{in}\\)\\:")

    f_id = fluids_techno.index(fluid)
    for i, p in enumerate(Tmax_techno[f_id]):
        label = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(ts_techno[i])+"}{\\K}"
        axs[j].plot(qs_techno, p, label=label, color=colors[f_id][i])

    for i, p in enumerate(Tmin_techno[f_id]):
        axs[j].plot(qs_techno, p, "--", color=colors[f_id][i])

    axs[j].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    axs[j].set_ylabel("Working fluid temperature/\\unit{\\K}")

    axs[j].set_ylim(300, 550)

axs[-1].legend()

tikzplotlib.save("Plots/SimpleORC_TmaxTmin.tex", figure=fig)


plt.show()
