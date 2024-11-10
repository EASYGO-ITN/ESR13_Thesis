import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib
from CoolProp.CoolProp import PropsSI

with open("../../04_SimpleORC_superheated_recuperated/sensitivity_results.json", "r") as file:
    results = json.load(file)

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

Pmax = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
Tmax = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
Tmin = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]
DTsh = [[[np.NAN + 0 for q in qs] for t in ts] for f in fluids]

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

qs = [q * 100 for q in qs]


colors = [plt.cm.Blues(np.linspace(0.3, 1, len(ts))),
          plt.cm.Oranges(np.linspace(0.3, 1, len(ts))),
          plt.cm.Greens(np.linspace(0.3, 1, len(ts))),
          plt.cm.Reds(np.linspace(0.3, 1, len(ts))),
          plt.cm.Purples(np.linspace(0.3, 1, len(ts))),
          plt.cm.Greys(np.linspace(0.3, 1, len(ts)))]


# plot the maximum pressure
fig, axs = plt.subplots(nrows=len(fluids))

# axs[-1].plot([0, 1], [0, 0], "k", label="\\(T_{max}\\)")
# axs[-1].plot([0, 1], [0, 0], "k--", label="\\(T_{min}\\)")
# axs[-1].plot([0, 1], [0, 0], "--", label="\\(T_{geo}^{in}\\)\\:")


for j, fluid in enumerate(fluids):
    axs[j].set_title("{}".format(fluid[0]))

    f_id = fluids.index(fluid)
    for i, p in enumerate(Pmax[f_id]):
        label = "\\quad\\qty{" + "{:0f}".format(ts[i]) + "}{\\K}"
        label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(ts[i]) + "}{\\K}"
        axs[j].plot(qs, p, label=label, color=colors[f_id][i])

    axs[j].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    axs[j].set_ylabel("Reduced Pressure")

    axs[j].set_ylim(0.25, 0.85)

axs[-1].legend()

tikzplotlib.save("Plots/SimpleORC_Pmax.tex", figure=fig)


# plot the maximum pressure
fig, axs = plt.subplots(nrows=len(fluids))
for j, fluid in enumerate(fluids):
    axs[j].set_title("{}".format(fluid[0]))

    f_id = fluids.index(fluid)
    for i, p in enumerate(DTsh[f_id]):
        label = "\\quad\\qty{" + "{:0f}".format(ts[i]) + "}{\\K}"
        label = "\\(T_{geo}^{in}=\\)\\qty{" + "{:.0f}".format(ts[i]) + "}{\\K}"
        axs[j].plot(qs, p, label=label, color=colors[f_id][i])

    axs[j].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    axs[j].set_ylabel("Superheating/\\unit{\\K}")

    # axs[j].set_ylim(0.25, 0.85)

axs[-1].legend()

tikzplotlib.save("Plots/SimpleORC_DTsh.tex", figure=fig)


fig, axs = plt.subplots(len(fluids))
for j, fluid in enumerate(fluids):
    axs[j].set_title("{}".format(fluid[0]))

    axs[j].plot([0, 1], [273, 273], "k", label="\\(T_{max}\\)")
    axs[j].plot([0, 1], [273, 273], "k--", label="\\(T_{min}\\)")
    # axs[j].plot([0, 1], [273, 273], "--", label="\\(T_{geo}^{in}\\)\\:")

    f_id = fluids.index(fluid)
    for i, p in enumerate(Tmax[f_id]):
        label = "\\(T_{geo}^{in}=\\)\\qty{"+"{:.0f}".format(ts[i])+"}{\\K}"
        axs[j].plot(qs, p, label=label, color=colors[f_id][i])

    for i, p in enumerate(Tmin[f_id]):
        axs[j].plot(qs, p, "--", color=colors[f_id][i])

    axs[j].set_xlabel("Inlet Steam Quality/\\unit{\\percent}")
    axs[j].set_ylabel("Working fluid temperature/\\unit{\\K}")

    axs[j].set_ylim(300, 550)





axs[-1].legend()

tikzplotlib.save("Plots/SimpleORC_TmaxTmin.tex", figure=fig)

plt.show()
